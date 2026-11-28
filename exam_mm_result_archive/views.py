import base64
import os
import uuid
from django.conf import settings
from rest_framework.renderers import BaseRenderer, JSONRenderer
from django.urls import reverse
from collections import OrderedDict, defaultdict

from django.db.models import Q

from rest_framework import generics, filters, pagination, parsers, serializers, status
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from apps.students.models import Student
from academic_mm_class_and_section.models import AcademicClass, Section
from exam_mm_exam_setup.models import ExamSetup
from exam_mm_exmroutine_exmadmit.utils import student_takes_subject, subject_is_optional
from .models import (
    ResultPublishSchedule,
    MarksEntryLog,
    ExamResultConfig,
    GradeScale,
    StudentExamResult,
    SubjectGroup,
    class_has_practical,
    grade_from_scale,
    pick_scale,
)
from .serializers import (
    ResultPublishScheduleSerializer,
    ExamResultConfigSerializer,
    GradeScaleSerializer,
    StudentExamResultSerializer,
    StudentListForResultSerializer,
    BulkResultInputSerializer,
    SubjectGroupSerializer,
    full_marks_for,
    sections_for_exam_class,
    to_decimal,
    validate_marks_entry,
)

RESULT_SELECT = (
    'result_config__exam_routine__subject',
    'result_config__exam_routine__exam_name',
    'result_config__exam_routine__academic_class',
    'section',
)


class ResultPagination(pagination.PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


# ---------------------------------------------------------------------------
# Result হিসাবের নিয়ম (marksheet, class summary, combined result সবাই এটাই ব্যবহার করে)
#
# - দুই পেপারের বিষয় (English, Bangla) SubjectGroup দিয়ে একটা বিষয় হিসেবে যোগ হয়।
# - ধর্ম বিষয়: ছাত্রের নিজের ধর্মেরটাই ধরা হয়।
# - ঐচ্ছিক (৪র্থ) বিষয় (Higher Math, Agriculture): fail করলেও result এ প্রভাব নেই;
#   GPA 2 এর বেশি হলে (GPA - 2) যোগ হয়।
# - অন্য যেকোনো বিষয়ে fail মানে পুরো result fail।
# - পূর্ণমান ও pass mark আসে exam routine ও result-config থেকে।
# - ক্লাস ৬-৮: written + mcq যোগ করে মোট নম্বরে pass/fail।
# - ক্লাস ৯-১০: written, mcq, practical প্রতিটায় আলাদা pass করতে হয়।
# - Grade তালিকা: exam + class + section অনুযায়ী সবচেয়ে নির্দিষ্টটা চলে (pick_scale)।
# ---------------------------------------------------------------------------
def overall_grade_from_cgpa(cgpa):
    if cgpa >= 5.0:
        return 'A+'
    elif cgpa >= 4.0:
        return 'A'
    elif cgpa >= 3.5:
        return 'A-'
    elif cgpa >= 3.0:
        return 'B'
    elif cgpa >= 2.0:
        return 'C'
    elif cgpa >= 1.0:
        return 'D'
    return 'F'


class ScaleBook:
    """একটা ক্লাসের সব grade তালিকা একবারে এনে রাখে (বারবার query না করার জন্য)।"""

    def __init__(self, academic_class_id):
        scales = GradeScale.objects.filter(
            Q(academic_class_id=academic_class_id) | Q(academic_class__isnull=True)
        ).prefetch_related('rows')
        self._subject, self._group = defaultdict(list), defaultdict(list)
        for s in scales:
            if s.group_id:
                self._group[s.group_id].append(s)
            elif s.subject_id:
                self._subject[s.subject_id].append(s)

    def for_subject(self, subject_id, exam_id=None, section_id=None):
        return pick_scale(self._subject.get(subject_id, []), exam_id, section_id)

    def for_group(self, group_id, exam_id=None, section_id=None):
        return pick_scale(self._group.get(group_id, []), exam_id, section_id)


def load_group_map():
    """{subject_id: SubjectGroup}"""
    mapping = {}
    for group in SubjectGroup.objects.prefetch_related('subjects'):
        for subject in group.subjects.all():
            mapping[subject.id] = group
    return mapping


def result_full_marks(res):
    return res.result_config.total_full_marks_calc


def _build_buckets(student, results, group_map):
    buckets, skipped = OrderedDict(), []
    ordered = sorted(results, key=lambda r: (r.result_config.exam_routine.exam_date, r.id))
    for res in ordered:
        routine = res.result_config.exam_routine
        subject = routine.subject
        if not student_takes_subject(student, subject):
            skipped.append(subject.name)
            continue
        group = group_map.get(subject.id)
        key = ('g', group.id) if group else ('s', subject.id)
        b = buckets.get(key)
        if b is None:
            b = buckets[key] = {
                'name': group.name if group else subject.name,
                'group_id': group.id if group else None,
                'subject_id': None if group else subject.id,
                'is_optional': False if group else subject_is_optional(subject),
                'papers': [], 'exams': [],
                'written': 0.0, 'mcq': 0.0, 'practical': 0.0, 'grace': 0.0, 'gw': 0.0, 'gm': 0.0, 'gp': 0.0,
                'written_pass': 0.0, 'mcq_pass': 0.0, 'practical_pass': 0.0, 'pass_total': 0.0,
                'total': 0.0, 'full': 0.0,
            }
        b['papers'].append(subject.name)
        b['exams'].append({
            'exam': routine.exam_name.name,
            'subject': subject.name,
            'marks': float(res.total_marks),
            'full_marks': result_full_marks(res),
            'grade': res.grade,
        })
        b['written'] += float(res.written_marks)
        b['mcq'] += float(res.mcq_marks)
        b['practical'] += float(res.practical_marks)
        b['grace'] += float(res.grace_marks)
        b['gw'] += float(res.grace_written)
        b['gm'] += float(res.grace_mcq)
        b['gp'] += float(res.grace_practical)
        cfg = res.result_config
        b['written_pass'] += float(cfg.written_pass_marks)
        b['mcq_pass'] += float(cfg.mcq_pass_marks)
        b['practical_pass'] += float(cfg.practical_pass_marks)
        b['pass_total'] += cfg.total_pass_marks_calc
        b['total'] += float(res.total_marks)
        b['full'] += result_full_marks(res)
    return buckets, skipped


def _evaluate(b, academic_class, scale_book, check_components, exam_id=None, section_id=None):
    if b['group_id']:
        scale = scale_book.for_group(b['group_id'], exam_id, section_id)
    else:
        scale = scale_book.for_subject(b['subject_id'], exam_id, section_id)
    total, full = b['total'], b['full']
    if scale:
        grade, point = grade_from_scale(scale, total, full)
        source = 'admin'
    else:
        # Scale না থাকলে নিজে থেকে grade বসানো হয় না
        grade, point = '', 0.0
        source = 'none'

    # admin এর দেওয়া মোট pass mark (পেপার যোগ করে) এর নিচে হলে fail
    below_total = b['pass_total'] > 0 and total < b['pass_total']
    if below_total:
        grade, point = 'F', 0.0

    passed = (point > 0 if scale else True) and not below_total
    failed_parts = []
    if check_components:
        if (b['written'] + b['gw']) < b['written_pass']:
            failed_parts.append('written')
        if (b['mcq'] + b['gm']) < b['mcq_pass']:
            failed_parts.append('mcq')
        if class_has_practical(academic_class) and (b['practical'] + b['gp']) < b['practical_pass']:
            failed_parts.append('practical')
        if failed_parts:
            # যেকোনো একটা অংশে fail করলে grade F, GPA 0
            grade, point, passed = 'F', 0.0, False

    return {
        'subject': b['name'],
        'papers': sorted(set(b['papers'])) if b['group_id'] else None,
        'is_optional': b['is_optional'],
        'written_marks': round(b['written'], 2),
        'mcq_marks': round(b['mcq'], 2),
        'practical_marks': round(b['practical'], 2),
        'failed_parts': failed_parts,
        'pass_marks': {'written': round(b['written_pass'], 2), 'mcq': round(b['mcq_pass'], 2),
                       'practical': round(b['practical_pass'], 2), 'total': round(b['pass_total'], 2)},
        'grace_written': round(b['gw'], 2),
        'grace_mcq': round(b['gm'], 2),
        'grace_practical': round(b['gp'], 2),
        'grace_marks': round(b['grace'], 2),
        'total_marks': round(total, 2),
        'full_marks': round(full, 2),
        'percentage': round((total / full) * 100, 2) if full > 0 else 0.0,
        'grade': grade,
        'gpa': float(point),
        'status': 'pass' if passed else 'fail',
        'grade_source': source,
        'exams': b['exams'],
    }


def summarize_student(student, results, academic_class, scale_book, group_map, check_components=True):
    """
    results: ওই ছাত্রের StudentExamResult এর তালিকা (select_related করা)।
    check_components=False দিলে (একাধিক পরীক্ষা যোগ করার সময়) written/mcq/practical আলাদা pass দেখা হয় না।
    Grade তালিকা: results একটাই exam এর হলে ওই exam এর তালিকা চলে; একাধিক exam মিলালে 'সব পরীক্ষার' তালিকা।
    """
    exam_ids = {r.result_config.exam_routine.exam_name_id for r in results}
    exam_id = next(iter(exam_ids)) if len(exam_ids) == 1 else None
    section_id = getattr(student, 'section_static_id', None)

    buckets, skipped = _build_buckets(student, results, group_map)
    rows = [
        _evaluate(b, academic_class, scale_book, check_components, exam_id, section_id)
        for b in buckets.values()
    ]

    main = [r for r in rows if not r['is_optional']]
    optional = [r for r in rows if r['is_optional']]
    warnings = []
    if skipped:
        warnings.append(f"ছাত্রের ধর্মের সাথে না মেলায় বাদ: {', '.join(sorted(set(skipped)))}")

    fourth = None
    if optional:
        optional.sort(key=lambda r: (r['status'] == 'pass', r['gpa']), reverse=True)
        fourth = optional[0]
        if len(optional) > 1:
            warnings.append(
                "একাধিক ঐচ্ছিক বিষয়ের নম্বর আছে: "
                + ", ".join(r['subject'] for r in optional)
                + f"। শুধু '{fourth['subject']}' ৪র্থ বিষয় ধরা হয়েছে।"
            )

    for r in main:
        r['counted_in'] = 'main'
        r['bonus_gpa'] = 0.0
    for r in optional:
        r['counted_in'] = 'fourth_subject' if r is fourth else 'ignored'
        r['bonus_gpa'] = 0.0

    count = len(main)
    no_scale = [r['subject'] for r in main if r['grade_source'] == 'none']
    if no_scale:
        warnings.append("Grade Scale নেই (grade/GPA হিসাব হয়নি): " + ", ".join(no_scale))
    all_main_passed = all(r['status'] == 'pass' for r in main)

    # ৪র্থ বিষয়ের bonus: শুধু ছাত্র পাস করলে আর ঐচ্ছিক বিষয়ে নিজে pass করলে, GPA - 2 (2 এর বেশি হলে)
    bonus = 0.0
    if fourth and count and all_main_passed and fourth['status'] == 'pass' and fourth['gpa'] > 2:
        bonus = round(fourth['gpa'] - 2, 2)
        fourth['bonus_gpa'] = bonus

    if count == 0:
        cgpa, overall_grade, overall_status = 0.0, '-', 'fail'
    elif not all_main_passed:
        cgpa, overall_grade, overall_status = 0.0, 'F', 'fail'
    elif no_scale:
        # কোনো বিষয়ে Grade Scale না থাকলে CGPA বানানো যায় না
        cgpa, overall_grade, overall_status = None, '-', 'pass'
    else:
        cgpa = min(5.0, round((sum(r['gpa'] for r in main) + bonus) / count, 2))
        overall_grade, overall_status = overall_grade_from_cgpa(cgpa), 'pass'

    all_rows = main + optional
    return {
        'subject_wise_results': all_rows,
        'summary': {
            'total_subjects': count,
            'grand_total_marks': round(sum(r['total_marks'] for r in all_rows), 2),
            'grand_full_marks': round(sum(r['full_marks'] for r in all_rows), 2),
            'cgpa': cgpa,
            'overall_grade': overall_grade,
            'overall_status': overall_status,
            'fourth_subject': (
                {'subject': fourth['subject'], 'gpa': fourth['gpa'], 'status': fourth['status'], 'bonus_gpa': bonus}
                if fourth else None
            ),
        },
        'warnings': warnings,
    }


def band_message(view, academic_class):
    """
    ক্লাস ৬-৮ ও ৯-১০ এর আলাদা API র জন্য: view এর band_min/band_max এর বাইরের ক্লাস হলে বার্তা দেয়।
    সাধারণ (আগের) API তে band_min = None, তাই কোনো সীমা নেই।
    """
    low, high = getattr(view, 'band_min', None), getattr(view, 'band_max', None)
    if low is None:
        return None
    value = getattr(academic_class, 'numeric_value', None)
    if value is None or not (low <= value <= high):
        return f"এই API শুধু {view.band_label} এর জন্য ('{academic_class}' এর জন্য নয়)।"
    return None


def band_filter(view, queryset, lookup):
    low, high = getattr(view, 'band_min', None), getattr(view, 'band_max', None)
    if low is None:
        return queryset
    return queryset.filter(**{f"{lookup}__numeric_value__range": (low, high)})


class ExamResultConfigListCreateView(generics.ListCreateAPIView):
    queryset = ExamResultConfig.objects.all().select_related('exam_routine')
    serializer_class = ExamResultConfigSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_queryset(self):
        return band_filter(self, super().get_queryset(), 'exam_routine__academic_class')

    def perform_create(self, serializer):
        message = band_message(self, serializer.validated_data['exam_routine'].academic_class)
        if message:
            raise serializers.ValidationError({'exam_routine': message})
        serializer.save()


class ExamResultConfigDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExamResultConfig.objects.all().select_related('exam_routine')
    serializer_class = ExamResultConfigSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_queryset(self):
        return band_filter(self, super().get_queryset(), 'exam_routine__academic_class')


def build_entry_info(config, student_ids):
    """
    এই বিষয়ে কে কখন নম্বর দিয়েছে তার সারাংশ (নাম, রোল, কতজনের, প্রথম/শেষ সময়) এবং কে শেষ বদলেছে।
    """
    logs = list(MarksEntryLog.objects.filter(result_config=config, student_id__in=student_ids).order_by('created_at', 'id'))
    groups = OrderedDict()
    last_by_student = {}
    last_edit = None
    for l in logs:
        if l.action == 'unchanged':
            continue
        key = (l.entered_by, l.entered_by_role)
        g = groups.setdefault(key, {'entered_by': l.entered_by or '-', 'role': l.entered_by_role or '-',
                                    'students': set(), 'first_at': l.created_at, 'last_at': l.created_at})
        g['students'].add(l.student_id)
        g['last_at'] = l.created_at
        last_by_student[l.student_id] = {'entered_by': l.entered_by or '-', 'entered_by_role': l.entered_by_role or '-',
                                         'entered_at': l.created_at}
        if l.action == 'updated':
            last_edit = {'entered_by': l.entered_by or '-', 'role': l.entered_by_role or '-', 'at': l.created_at}
    return {
        'entered_by': [{**{k: v for k, v in g.items() if k != 'students'}, 'student_count': len(g['students'])}
                       for g in groups.values()],
        'last_edited_by': last_edit,
        '_last_by_student': last_by_student,
    }


class StudentListByClassSectionView(generics.GenericAPIView):
    serializer_class = StudentListForResultSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('class_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('section_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('result_config_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
        ]
    )
    def get(self, request, *args, **kwargs):
        class_id = request.query_params.get('class_id')
        section_id = request.query_params.get('section_id')
        result_config_id = request.query_params.get('result_config_id')

        if not class_id:
            return Response({'error': 'class_id is required'}, status=400)

        try:
            academic_class = AcademicClass.objects.get(id=class_id)
        except AcademicClass.DoesNotExist:
            return Response({'error': 'Class not found'}, status=404)

        message = band_message(self, academic_class)
        if message:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

        students = Student.objects.filter(class_name_static=academic_class)

        section = None
        if section_id:
            try:
                section = Section.objects.get(id=section_id)
            except Section.DoesNotExist:
                return Response({'error': 'Section not found'}, status=404)
            students = students.filter(section_static=section)

        config = None
        config_data = None
        if result_config_id:
            try:
                config = ExamResultConfig.objects.select_related(
                    'exam_routine__exam_setup', 'exam_routine__subject'
                ).get(id=result_config_id)
            except ExamResultConfig.DoesNotExist:
                return Response({'error': 'Result config not found'}, status=404)

            if config.exam_routine.academic_class_id != academic_class.id:
                return Response(
                    {'error': 'এই result config অন্য class এর।'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            setup = config.exam_routine.exam_setup
            if setup:
                setup_sections = setup.sections.all()
                if section and not setup_sections.filter(id=section.id).exists():
                    return Response(
                        {'error': 'এই section এই exam setup এ নেই।'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                students = students.filter(section_static__in=setup_sections)

            config_data = ExamResultConfigSerializer(config).data

        students = list(students.order_by('roll_number'))

        # ধর্ম বিষয়ের নম্বর দিতে গেলে শুধু ওই ধর্মের ছাত্র আসবে
        if config:
            students = [s for s in students if student_takes_subject(s, config.exam_routine.subject)]

        student_list = []
        for student in students:
            # জমা হওয়া নম্বর এখানে দেখানো হয় না (গোপন) — শুধু জানানো হয় জমা হয়েছে। নম্বর দেখা যাবে ফলাফলে।
            existing_result = None
            if config:
                result = StudentExamResult.objects.filter(
                    student=student,
                    result_config=config
                ).only('id').first()
                if result:
                    existing_result = {'entered': True, 'result_id': result.id}

            student_list.append({
                'id': student.id,
                'full_name': student.full_name,
                'roll_number': student.roll_number,
                'admission_number': student.admission_number,
                'religion': student.religion,
                'existing_result': existing_result,
            })

        # কে নম্বর দিয়েছে — উপরে (students এর আগে) দেখানোর জন্য
        entry_info = None
        if config:
            entry_info = build_entry_info(config, [s.id for s in students])
            for item, student in zip(student_list, students):
                if item['existing_result'] is not None:
                    info = entry_info['_last_by_student'].get(student.id)
                    if info:
                        item['existing_result'].update(info)
            entry_info.pop('_last_by_student', None)

        return Response(OrderedDict([
            ('class', academic_class.name),
            ('has_practical', class_has_practical(academic_class)),
            ('result_config', config_data),
            ('entry_info', entry_info),
            ('students', student_list),
        ]))


class StudentExamResultListCreateView(generics.ListCreateAPIView):
    serializer_class = StudentExamResultSerializer
    pagination_class = ResultPagination
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['student__first_name', 'student__last_name', 'overall_status']

    def perform_create(self, serializer):
        result = serializer.save()
        log_marks_entry(uuid.uuid4(), result.result_config, result.student, result, None, self.request, True)

    def get_queryset(self):
        queryset = StudentExamResult.objects.all().select_related('student', 'result_config', 'section')
        config_id = self.request.query_params.get('result_config')
        section_id = self.request.query_params.get('section')
        overall_status = self.request.query_params.get('overall_status')

        if config_id:
            queryset = queryset.filter(result_config_id=config_id)
        if section_id:
            queryset = queryset.filter(section_id=section_id)
        if overall_status:
            queryset = queryset.filter(overall_status=overall_status)

        return queryset


class StudentExamResultDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentExamResult.objects.all().select_related('student', 'result_config')
    serializer_class = StudentExamResultSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def perform_update(self, serializer):
        # Edit: সংশোধন হলে log এ updated + আগের মান জমা থাকে
        inst = serializer.instance
        old = (inst.written_marks, inst.mcq_marks, inst.practical_marks)
        result = serializer.save()
        log_marks_entry(uuid.uuid4(), result.result_config, result.student, result, old, self.request, False)


def _who_info(request):
    """যে নম্বর দিচ্ছে: (নাম, রোল, user id)। লগইন না থাকলে ফাঁকা।"""
    user = getattr(request, 'user', None)
    if user is None or not getattr(user, 'is_authenticated', False):
        return '', '', None
    name = ''
    try:
        name = (user.get_full_name() or '').strip()
    except Exception:
        pass
    name = (name or user.get_username())[:150]

    role = ''
    r = getattr(user, 'role', None)
    if r:
        role = getattr(r, 'name', None) or getattr(r, 'title', None) or str(r)
    if not role and hasattr(user, 'groups'):
        try:
            g = user.groups.first()
            role = g.name if g else ''
        except Exception:
            role = ''
    if not role:
        if getattr(user, 'is_superuser', False):
            role = 'Admin'
        elif getattr(user, 'is_staff', False):
            role = 'Staff'
    return name, str(role)[:80], getattr(user, 'pk', None)


def _who(request):
    return _who_info(request)[0]


def log_marks_entry(batch_id, config, student, result, old, request, is_created):
    """old = (written, mcq, practical) আগের মান, নতুন হলে None।"""
    new = (result.written_marks, result.mcq_marks, result.practical_marks)
    if is_created:
        action = 'created'
    elif old is not None and tuple(old) == tuple(new):
        action = 'unchanged'
    else:
        action = 'updated'
    MarksEntryLog.objects.create(
        batch_id=batch_id, result_config=config, student=student, action=action,
        old_written=old[0] if old else None, old_mcq=old[1] if old else None,
        old_practical=old[2] if old else None,
        new_written=new[0], new_mcq=new[1], new_practical=new[2],
        new_total=result.total_marks, new_grade=result.grade,
        entered_by=_who_info(request)[0], entered_by_role=_who_info(request)[1], entered_by_id=_who_info(request)[2],
    )


class BulkResultInputView(generics.GenericAPIView):
    serializer_class = BulkResultInputSerializer
    parser_classes = [parsers.JSONParser]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        results = data['results']

        try:
            config = ExamResultConfig.objects.select_related(
                'exam_routine__exam_setup', 'exam_routine__subject', 'exam_routine__academic_class'
            ).get(id=data['result_config'])
        except ExamResultConfig.DoesNotExist:
            return Response({'error': 'Result config not found'}, status=404)

        message = band_message(self, config.exam_routine.academic_class)
        if message:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

        created = []
        updated = []
        errors = []
        batch_id = uuid.uuid4()

        for item in results:
            student_id = item.get('student')

            written, err1 = to_decimal(item.get('written_marks', 0), 'Written')
            mcq, err2 = to_decimal(item.get('mcq_marks', 0), 'MCQ')
            practical, err3 = to_decimal(item.get('practical_marks', 0), 'Practical')
            number_error = err1 or err2 or err3
            if number_error:
                errors.append({'student': student_id, 'error': number_error})
                continue
            if not config.has_practical:
                practical = to_decimal(0, '')[0]

            try:
                student = Student.objects.get(id=student_id)
            except Student.DoesNotExist:
                errors.append({'student': student_id, 'error': 'Student not found'})
                continue

            error = validate_marks_entry(student, config, written, mcq, practical)
            if error:
                errors.append({'student': student_id, 'error': error})
                continue

            # একবার জমা (Save) হয়ে গেলে এই API দিয়ে আর নম্বর জমা/বদলানো যায় না — বদলাতে Edit (results/<id>/) ব্যবহার করতে হবে
            if StudentExamResult.objects.filter(result_config=config, student=student).exists():
                errors.append({
                    'student': student_id,
                    'code': 'already_submitted',
                    'error': 'এই ছাত্রের নম্বর আগেই জমা হয়েছে। বদলাতে Edit ব্যবহার করুন (অনুমতি লাগবে)।',
                })
                continue

            result = StudentExamResult.objects.create(
                result_config=config,
                student=student,
                written_marks=written,
                mcq_marks=mcq,
                practical_marks=practical,
                section=student.section_static,
            )

            log_marks_entry(batch_id, config, student, result, None, request, True)
            created.append(student_id)

        return Response({
            'message': f'{len(created)} created, {len(updated)} updated, {len(errors)} errors',
            'batch_id': str(batch_id) if created else None,
            'receipt_url': (request.build_absolute_uri(reverse('marks-entry-receipt')) + f'?batch={batch_id}') if created else None,
            'created': created,
            'updated': updated,
            'errors': errors,
        }, status=status.HTTP_200_OK)


class RecalculateResultsView(APIView):
    """
    পুরোনো সংরক্ষিত result গুলোর grade/GPA/pass-fail নতুন নিয়মে আবার হিসাব করে।
    body: { "result_config": 5 } অথবা { "exam_setup": 3 }
    """

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'result_config': openapi.Schema(type=openapi.TYPE_INTEGER),
            'exam_setup': openapi.Schema(type=openapi.TYPE_INTEGER),
        },
    ))
    def post(self, request):
        config_id = request.data.get('result_config')
        setup_id = request.data.get('exam_setup')
        if not config_id and not setup_id:
            return Response({'error': 'result_config অথবা exam_setup দিন।'}, status=400)

        qs = StudentExamResult.objects.select_related(
            'result_config__exam_routine__subject', 'result_config__exam_routine__academic_class'
        )
        qs = qs.filter(result_config_id=config_id) if config_id else qs.filter(
            result_config__exam_routine__exam_setup_id=setup_id
        )
        count = 0
        for res in qs:
            res.save()
            count += 1
        return Response({'recalculated': count})


class GraceMarksApplyView(APIView):
    """
    Grace marks একসাথে বসানো। written, mcq, practical প্রতিটা আলাদা করে দেওয়া যায়
    (practical শুধু ক্লাস ৯-১০ এর জন্য)। মোট নম্বরে আলাদা কোনো সংখ্যা যোগ হয় না,
    প্রতিটা অংশের grace ওই অংশের নম্বরের সাথে যোগ হয় (ওই অংশের পূর্ণমান ছাড়ায় না)।
    বসানোর পর ওই exam এর সব result নিজে থেকে আবার হিসাব হয়।

    body: { "exam_setup": 5, "grace_written": 3, "grace_mcq": 2 }               → ওই setup এর সব বিষয়ে
          { "exam_setup": 5, "grace_written": 3, "grace_mcq": 2,
            "grace_practical": 1, "subject": 21 }                                → শুধু একটি বিষয়ে
          { "exam_setup": 5, "grace_written": 0, "grace_mcq": 0 }               → grace তুলে দিতে
    যে field পাঠানো হবে শুধু সেটাই বদলাবে, না পাঠালে আগেরটাই থাকবে।
    """

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['exam_setup'],
        properties={
            'exam_setup': openapi.Schema(type=openapi.TYPE_INTEGER),
            'subject': openapi.Schema(type=openapi.TYPE_INTEGER, description='ঐচ্ছিক (না দিলে সব বিষয়)'),
            'grace_written': openapi.Schema(type=openapi.TYPE_NUMBER),
            'grace_mcq': openapi.Schema(type=openapi.TYPE_NUMBER),
            'grace_practical': openapi.Schema(type=openapi.TYPE_NUMBER, description='শুধু ক্লাস ৯-১০'),
        },
    ))
    def post(self, request):
        setup_id = request.data.get('exam_setup')
        if not setup_id:
            return Response({'error': 'exam_setup দিন।'}, status=400)

        values = {}
        for field, label in (('grace_written', 'Written grace'), ('grace_mcq', 'MCQ grace'),
                             ('grace_practical', 'Practical grace')):
            raw = request.data.get(field)
            if raw is None or raw == '':
                continue
            val, err = to_decimal(raw, label)
            if err:
                return Response({'error': err}, status=400)
            if val < 0:
                return Response({'error': f'{label} ঋণাত্মক হতে পারবে না।'}, status=400)
            values[field] = val
        if not values:
            return Response({'error': 'grace_written, grace_mcq বা grace_practical এর অন্তত একটা দিন।'},
                            status=400)

        setup = ExamSetup.objects.filter(id=setup_id).select_related('academic_class').first()
        if not setup:
            return Response({'error': 'Exam setup পাওয়া যায়নি।'}, status=404)
        if values.get('grace_practical', 0) > 0 and not class_has_practical(setup.academic_class):
            return Response({'error': 'এই ক্লাসে practical নেই, তাই grace_practical দেওয়া যাবে না (শুধু ক্লাস ৯-১০)।'},
                            status=400)

        configs = ExamResultConfig.objects.filter(exam_routine__exam_setup_id=setup_id)
        subject_id = request.data.get('subject')
        if subject_id:
            configs = configs.filter(exam_routine__subject_id=subject_id)
        config_ids = list(configs.values_list('id', flat=True))
        if not config_ids:
            return Response({'error': 'এই exam setup এ কোনো result config পাওয়া যায়নি। আগে result-config বানান।'},
                            status=404)

        configs.update(**values)
        count = 0
        for res in StudentExamResult.objects.filter(result_config_id__in=config_ids).select_related(
            'result_config__exam_routine__subject', 'result_config__exam_routine__academic_class'
        ):
            res.save()
            count += 1
        return Response({'configs_updated': len(config_ids), 'results_recalculated': count,
                         **{k: float(v) for k, v in values.items()}})


def _result_queryset():
    return StudentExamResult.objects.select_related(*RESULT_SELECT)


class StudentDetailedMarksheetView(APIView):

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('exam_setup_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True,
                              description="কোন পরীক্ষার marksheet (Exam Setup ID)"),
        ]
    )
    def get(self, request, student_id):
        setup_id = request.query_params.get('exam_setup_id')
        if not setup_id:
            return Response({'error': 'exam_setup_id দিন।'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            student = Student.objects.select_related('class_name_static', 'section_static').get(id=student_id)
        except Student.DoesNotExist:
            return Response({'error': 'ছাত্র পাওয়া যায়নি।'}, status=status.HTTP_404_NOT_FOUND)

        results = list(_result_queryset().filter(
            student=student, result_config__exam_routine__exam_setup_id=setup_id
        ))
        if not results:
            return Response(
                {"error": "এই স্টুডেন্টের এই পরীক্ষার কোনো রেজাল্ট পাওয়া যায়নি।"},
                status=status.HTTP_404_NOT_FOUND
            )

        academic_class = student.class_name_static
        message = band_message(self, academic_class)
        if message:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)
        data = summarize_student(
            student, results, academic_class, ScaleBook(academic_class.id), load_group_map()
        )
        section = student.section_static
        return Response({
            "student_id": student.id,
            "student_name": getattr(student, 'full_name', str(student)),
            "roll_number": getattr(student, 'roll_number', ''),
            "section": getattr(section, 'name', '') if section else '',
            **data,
        }, status=status.HTTP_200_OK)


class ClassSectionResultSummaryView(APIView):

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('class_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True, description="Class ID"),
            openapi.Parameter('exam_setup_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False,
                              description="কোন পরীক্ষার result (Exam Setup ID)। result_config_id না দিলে এটা লাগবে"),
            openapi.Parameter('section_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False, description="Section ID (Optional)"),
            openapi.Parameter('result_config_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False,
                              description="শুধু একটা বিষয়ের result দেখতে (Optional)"),
        ]
    )
    def get(self, request):
        class_id = request.query_params.get('class_id')
        section_id = request.query_params.get('section_id')
        result_config_id = request.query_params.get('result_config_id')
        setup_id = request.query_params.get('exam_setup_id')

        if not class_id:
            return Response({'error': 'class_id প্রদান করা বাধ্যতামূলক।'}, status=status.HTTP_400_BAD_REQUEST)
        if not setup_id and not result_config_id:
            return Response({'error': 'exam_setup_id (অথবা result_config_id) প্রদান করুন।'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            academic_class = AcademicClass.objects.get(id=class_id)
        except AcademicClass.DoesNotExist:
            return Response({'error': 'ক্লাসটি খুঁজে পাওয়া যায়নি।'}, status=status.HTTP_404_NOT_FOUND)

        message = band_message(self, academic_class)
        if message:
            return Response({'error': message}, status=status.HTTP_400_BAD_REQUEST)

        students = Student.objects.filter(class_name_static=academic_class, status="active")

        if setup_id:
            try:
                setup = ExamSetup.objects.get(id=setup_id, academic_class=academic_class)
            except ExamSetup.DoesNotExist:
                return Response({'error': 'Exam setup পাওয়া যায়নি বা অন্য class এর।'},
                                status=status.HTTP_404_NOT_FOUND)
            setup_sections = setup.sections.all()
            if section_id and not setup_sections.filter(id=section_id).exists():
                return Response({'error': 'এই section এই exam setup এ নেই।'}, status=status.HTTP_400_BAD_REQUEST)
            students = students.filter(section_static__in=setup_sections)

        section_obj = None
        if section_id:
            try:
                section_obj = Section.objects.get(id=section_id)
                students = students.filter(section_static=section_obj)
            except Section.DoesNotExist:
                return Response({'error': 'সেকশনটি খুঁজে পাওয়া যায়নি।'}, status=status.HTTP_404_NOT_FOUND)

        if request.query_params.get('student_id'):
            students = students.filter(id=request.query_params.get('student_id'))
        students = list(students.select_related('section_static').order_by('roll_number'))

        results_qs = _result_queryset().filter(student__in=students)
        if result_config_id:
            results_qs = results_qs.filter(result_config_id=result_config_id)
        if setup_id:
            results_qs = results_qs.filter(result_config__exam_routine__exam_setup_id=setup_id)
        by_student = defaultdict(list)
        for res in results_qs:
            by_student[res.student_id].append(res)

        scale_book, group_map = ScaleBook(academic_class.id), load_group_map()

        student_list = []
        for student in students:
            data = summarize_student(student, by_student.get(student.id, []), academic_class, scale_book, group_map)
            student_list.append({
                "student_id": student.id,
                "student_name": getattr(student, 'full_name', str(student)),
                "roll_number": getattr(student, 'roll_number', ''),
                "section": getattr(student.section_static, 'name', '') if student.section_static else '',
                **data,
            })

        return Response({
            "class": academic_class.name,
            "section": section_obj.name if section_obj else "All Sections",
            "total_students": len(student_list),
            "students": student_list
        }, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# Admin: বিষয় গ্রুপ ও Grade তালিকা
# ---------------------------------------------------------------------------
class SubjectGroupListCreateView(generics.ListCreateAPIView):
    queryset = SubjectGroup.objects.prefetch_related('subjects')
    serializer_class = SubjectGroupSerializer
    pagination_class = None


class SubjectGroupDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubjectGroup.objects.prefetch_related('subjects')
    serializer_class = SubjectGroupSerializer


def recalc_results_for_scale(scale):
    """
    Grade তালিকা বানানো/বদলানো/মোছার পর, ওই তালিকা যেসব সংরক্ষিত নম্বরে খাটে সেগুলোর grade সাথে সাথে আবার হিসাব হয়
    (না হলে পুরোনো সংরক্ষিত grade ডিফল্ট তালিকার মতোই থেকে যায়)। গ্রুপের তালিকা result দেখার সময় হিসাব হয়, তাই সেটা লাগে না।
    """
    if not scale.subject_id:
        return 0
    qs = StudentExamResult.objects.filter(
        result_config__exam_routine__subject_id=scale.subject_id
    ).select_related('result_config__exam_routine__subject', 'result_config__exam_routine__academic_class', 'student')
    if scale.academic_class_id:
        qs = qs.filter(result_config__exam_routine__academic_class_id=scale.academic_class_id)
    if scale.exam_name_id:
        qs = qs.filter(result_config__exam_routine__exam_name_id=scale.exam_name_id)
    if scale.section_id:
        qs = qs.filter(student__section_static_id=scale.section_id)
    count = 0
    for res in qs:
        res.save()
        count += 1
    return count


class GradeScaleListCreateView(generics.ListCreateAPIView):
    serializer_class = GradeScaleSerializer
    pagination_class = None

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('subject', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        openapi.Parameter('group', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        openapi.Parameter('exam_name', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        openapi.Parameter('academic_class', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        openapi.Parameter('section', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
    ])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def perform_create(self, serializer):
        scale = serializer.save()
        recalc_results_for_scale(scale)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return GradeScale.objects.none()
        qs = GradeScale.objects.select_related(
            'subject', 'group', 'exam_name', 'academic_class', 'section'
        ).prefetch_related('rows', 'group__subjects')
        p = self.request.query_params
        if p.get('subject'):
            qs = qs.filter(subject_id=p['subject'])
        if p.get('group'):
            qs = qs.filter(group_id=p['group'])
        if p.get('exam_name'):
            qs = qs.filter(exam_name_id=p['exam_name'])
        if p.get('academic_class'):
            qs = qs.filter(academic_class_id=p['academic_class'])
        if p.get('section'):
            qs = qs.filter(section_id=p['section'])
        return qs


class GradeScaleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GradeScale.objects.select_related(
        'subject', 'group', 'exam_name', 'academic_class', 'section'
    ).prefetch_related('rows', 'group__subjects')
    serializer_class = GradeScaleSerializer

    def perform_update(self, serializer):
        scale = serializer.save()
        recalc_results_for_scale(scale)

    def perform_destroy(self, instance):
        info = GradeScale(subject_id=instance.subject_id, academic_class_id=instance.academic_class_id,
                          exam_name_id=instance.exam_name_id, section_id=instance.section_id)
        instance.delete()
        recalc_results_for_scale(info)


class GradeScaleOptionsView(APIView):
    """
    Grade scale ফর্মের জন্য: exam ও class বাছার পর এটা ডাকলে
      - ওই exam setup এর সেকশনগুলো অটোমেটিক আসে (sections)
      - ক্লাস ৯-১০ হলে has_section_choice = true (UI তে section বাছার অপশন দেখান)
      - subject/group দিলে সর্বোচ্চ নম্বর (max_marks) আসে: exam routine এর total_marks, গ্রুপ হলে পেপারগুলোর যোগফল
    """

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('exam_name', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True),
        openapi.Parameter('academic_class', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True),
        openapi.Parameter('subject', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('group', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
    ])
    def get(self, request):
        p = request.query_params
        exam_id, class_id = p.get('exam_name'), p.get('academic_class')
        if not exam_id or not class_id:
            return Response({'error': 'exam_name ও academic_class দিন।'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            academic_class = AcademicClass.objects.get(id=class_id)
        except AcademicClass.DoesNotExist:
            return Response({'error': 'ক্লাসটি খুঁজে পাওয়া যায়নি।'}, status=status.HTTP_404_NOT_FOUND)

        if not ExamSetup.objects.filter(exam_name_id=exam_id, academic_class_id=class_id).exists():
            return Response({'error': 'এই exam ও class এর কোনো exam setup নেই।'}, status=status.HTTP_404_NOT_FOUND)

        max_marks = None
        group_id, subject_id = p.get('group'), p.get('subject')
        if group_id:
            try:
                group = SubjectGroup.objects.prefetch_related('subjects').get(id=group_id)
            except SubjectGroup.DoesNotExist:
                return Response({'error': 'Subject group পাওয়া যায়নি।'}, status=status.HTTP_404_NOT_FOUND)
            max_marks = full_marks_for([s.id for s in group.subjects.all()], exam_id, class_id)
        elif subject_id:
            max_marks = full_marks_for([int(subject_id)], exam_id, class_id)

        return Response({
            'exam_name': int(exam_id),
            'academic_class': {'id': academic_class.id, 'name': academic_class.name},
            'has_section_choice': class_has_practical(academic_class),
            'sections': sections_for_exam_class(exam_id, class_id),
            'max_marks': str(max_marks) if max_marks is not None else None,
        })


# ---------------------------------------------------------------------------
# ক্লাস ৬-৮ ও ক্লাস ৯-১০ এর আলাদা API (একই হিসাব, শুধু ক্লাসের সীমা বাঁধা)
#   ৬-৮ : written + mcq (practical নেই)
#   ৯-১০: written + mcq + practical
# ---------------------------------------------------------------------------
class Band68:
    band_min, band_max, band_label = 6, 8, 'ক্লাস ৬-৮'


class Band910:
    band_min, band_max, band_label = 9, 10, 'ক্লাস ৯-১০'


# ----- ক্লাস ৬-৮
class Class68ResultConfigListCreateView(Band68, ExamResultConfigListCreateView):
    pass


class Class68ResultConfigDetailView(Band68, ExamResultConfigDetailView):
    pass


class Class68StudentListView(Band68, StudentListByClassSectionView):
    pass


class Class68BulkResultInputView(Band68, BulkResultInputView):
    pass


class Class68StudentMarksheetView(Band68, StudentDetailedMarksheetView):
    pass


class Class68ResultSummaryView(Band68, ClassSectionResultSummaryView):
    pass


# ----- ক্লাস ৯-১০
class Class910ResultConfigListCreateView(Band910, ExamResultConfigListCreateView):
    pass


class Class910ResultConfigDetailView(Band910, ExamResultConfigDetailView):
    pass


class Class910StudentListView(Band910, StudentListByClassSectionView):
    pass


class Class910BulkResultInputView(Band910, BulkResultInputView):
    pass


class Class910StudentMarksheetView(Band910, StudentDetailedMarksheetView):
    pass


class Class910ResultSummaryView(Band910, ClassSectionResultSummaryView):
    pass


# ---------------------------------------------------------------------------
# Marks entry log ও রিসিপ্ট (কে কখন কত নম্বর দিল, পরে বদলালে ধরার জন্য)
# ---------------------------------------------------------------------------
def _fm(x):
    if x is None:
        return '-'
    x = float(x)
    return str(int(x)) if x == int(x) else f'{x:g}'


class BinaryPDFRenderer(BaseRenderer):
    media_type = 'application/pdf'
    format = 'pdf'
    charset = None
    render_style = 'binary'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


def load_font_base64():
    path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'SolaimanLipi.ttf')
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    return ''


SCHOOL_NAME = "Harikhali High School"


class MarksEntryLogView(APIView):
    """GET ?result_config=ID[&student=ID][&batch=UUID] → save/update এর ইতিহাস (JSON)"""

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('result_config', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('student', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('batch', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False),
    ])
    def get(self, request):
        qs = _log_queryset(request)
        if qs is None:
            return Response({'error': 'result_config অথবা batch দিন।'}, status=400)
        rows = [{
            'batch_id': str(l.batch_id), 'time': l.created_at, 'action': l.action,
            'student_id': l.student_id, 'student': getattr(l.student, 'full_name', str(l.student)),
            'roll': l.student.roll_number, 'entered_by': l.entered_by, 'entered_by_role': l.entered_by_role,
            'old': None if l.old_written is None else {
                'written': float(l.old_written), 'mcq': float(l.old_mcq), 'practical': float(l.old_practical)},
            'new': {'written': float(l.new_written), 'mcq': float(l.new_mcq),
                    'practical': float(l.new_practical), 'total': float(l.new_total), 'grade': l.new_grade},
        } for l in qs[:1000]]
        return Response({'count': len(rows), 'logs': rows})


def _log_queryset(request):
    qs = MarksEntryLog.objects.select_related(
        'student', 'result_config__exam_routine__subject', 'result_config__exam_routine__exam_name',
        'result_config__exam_routine__academic_class')
    batch = request.query_params.get('batch')
    config_id = request.query_params.get('result_config')
    student_id = request.query_params.get('student')
    if not batch and not config_id:
        return None
    if batch:
        qs = qs.filter(batch_id=batch)
    if config_id:
        qs = qs.filter(result_config_id=config_id)
    if student_id:
        qs = qs.filter(student_id=student_id)
    return qs


class MarksReceiptView(APIView):
    """
    Marks entry রিসিপ্ট PDF (কোন তারিখে, কোন বিষয়ে, কাকে কত নম্বর দেওয়া হলো)।
    ?batch=UUID         → ওই একবারের save এর রিসিপ্ট (save করার response এ batch_id আসে)
    ?result_config=ID   → ওই বিষয়ের সব save/update এর পুরো ইতিহাস
    ?output=html        → PDF এর বদলে HTML দেখতে
    """
    renderer_classes = [JSONRenderer, BinaryPDFRenderer]
    produces = ['application/pdf']

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('batch', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False),
        openapi.Parameter('result_config', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('output', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False,
                          description='pdf (default) / html'),
    ])
    def get(self, request):
        import html as _html
        from django.http import HttpResponse
        from django.utils import timezone

        qs = _log_queryset(request)
        if qs is None:
            return Response({'error': 'batch অথবা result_config দিন।'}, status=400)
        logs = list(qs.order_by('created_at', 'id'))
        if not logs:
            return Response({'error': 'কোনো রেকর্ড পাওয়া যায়নি।'}, status=404)

        first = logs[0]
        routine = first.result_config.exam_routine
        e = _html.escape
        multi = len({l.batch_id for l in logs}) > 1
        rows = ''
        for i, l in enumerate(sorted(logs, key=lambda x: (x.student.roll_number or '', x.created_at)), 1):
            t = timezone.localtime(l.created_at).strftime('%d-%m-%Y %I:%M %p')
            old = '' if l.old_written is None else (
                f"{_fm(l.old_written)} / {_fm(l.old_mcq)} / {_fm(l.old_practical)}")
            label = {'created': 'New', 'updated': 'Changed', 'unchanged': 'Same'}.get(l.action, l.action)
            rows += (f"<tr class='{l.action}'><td>{i}</td><td>{e(str(l.student.roll_number or ''))}</td>"
                     f"<td class='n'>{e(getattr(l.student, 'full_name', str(l.student)))}</td>"
                     f"<td>{_fm(l.new_written)}</td><td>{_fm(l.new_mcq)}</td><td>{_fm(l.new_practical)}</td>"
                     f"<td><b>{_fm(l.new_total)}</b></td><td>{e(l.new_grade)}</td>"
                     f"<td>{label}</td><td>{e(old)}</td><td>{e(l.entered_by or '-')}{(' (' + e(l.entered_by_role) + ')') if l.entered_by_role else ''}</td><td>{t}</td></tr>")

        font = load_font_base64()
        font_css = ("@font-face{font-family:'SolaimanLipi';src:url(data:font/ttf;base64,%s) format('truetype');}" % font
                    if font else '')
        printed = timezone.localtime().strftime('%d-%m-%Y %I:%M %p')
        title = 'Marks Entry History' if multi else 'Marks Entry Receipt'
        doc = f"""<!doctype html><html><head><meta charset='utf-8'><style>
{font_css}
@page{{size:A4 landscape;margin:10mm}}
body{{font-family:'SolaimanLipi',Arial,sans-serif;font-size:11px;color:#111}}
h1{{text-align:center;margin:0;font-size:20px}} h2{{text-align:center;margin:2px 0 8px;font-size:14px}}
.meta{{display:flex;flex-wrap:wrap;gap:4px 24px;border:1px solid #333;padding:6px 10px;margin-bottom:8px}}
table{{width:100%;border-collapse:collapse}} th,td{{border:1px solid #444;padding:3px 4px;text-align:center}}
th{{background:#e8ecf5}} td.n{{text-align:left}} tr.updated td{{background:#fff3cd}} tr.created td{{background:#eefaf0}}
.foot{{margin-top:8px;font-size:10px;color:#444}}
</style></head><body>
<h1>{e(SCHOOL_NAME)}</h1><h2>{title}</h2>
<div class='meta'><div><b>Exam:</b> {e(routine.exam_name.name)}</div>
<div><b>Class:</b> {e(routine.academic_class.name)}</div>
<div><b>Subject:</b> {e(routine.subject.name)}</div>
<div><b>Printed:</b> {printed}</div></div>
<table><tr><th>#</th><th>Roll</th><th>Student</th><th>Written</th><th>MCQ</th><th>Practical</th><th>Total</th>
<th>Grade</th><th>Status</th><th>Before (W/M/P)</th><th>Entered by</th><th>Date &amp; time</th></tr>{rows}</table>
<div class='foot'>Yellow = marks changed after earlier entry. This receipt is system generated.</div>
</body></html>"""

        if request.query_params.get('output') == 'html':
            return HttpResponse(doc, content_type='text/html; charset=utf-8')

        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=[
                '--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage',
                '--disable-gpu', '--no-zygote', '--single-process'])
            try:
                page = browser.new_context().new_page()
                page.set_content(doc, wait_until='load')
                pdf = page.pdf(format='A4', landscape=True, print_background=True, prefer_css_page_size=True)
            finally:
                browser.close()
        resp = HttpResponse(pdf, content_type='application/pdf')
        name = f"MarksReceipt_config{first.result_config_id}_{timezone.localtime():%Y%m%d_%H%M}.pdf"
        resp['Content-Disposition'] = f'attachment; filename="{name}"'
        return resp


# ---------------------------------------------------------------------------
# ফেল করা ছাত্রের তালিকা (ক্লাস/সেকশন/exam অনুযায়ী) — দেখা ও PDF ডাউনলোড
# ---------------------------------------------------------------------------
class _Params:
    """আরেকটা view এর get() কে ভেতর থেকে ডাকতে হালকা request।"""
    def __init__(self, data):
        self.query_params = data


def html_to_pdf(doc, landscape=True):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            '--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage',
            '--disable-gpu', '--no-zygote', '--single-process'])
        try:
            page = browser.new_context().new_page()
            page.set_content(doc, wait_until='load')
            return page.pdf(format='A4', landscape=landscape, print_background=True, prefer_css_page_size=True)
        finally:
            browser.close()


def failed_summary_data(class_id, setup_id, section_id=None):
    """
    ছাত্রের নাম ছাড়া সারাংশ: সেকশন → বিষয় → অংশ (Written/MCQ/Practical) অনুযায়ী
    কত নম্বর পেয়ে কতজন ফেল (যেমন 32 পেয়ে 5 জন, 31 পেয়ে 2 জন)।
    """
    params = {'class_id': class_id, 'exam_setup_id': setup_id}
    if section_id:
        params['section_id'] = section_id
    resp = ClassSectionResultSummaryView().get(_Params(params))
    if resp.status_code != 200:
        return None, None, resp
    data = resp.data
    PART = (('written', 'Written'), ('mcq', 'MCQ'), ('practical', 'Practical'))

    tree = OrderedDict()  # section -> subject -> {appeared, failed, parts{}, total{}}
    for st in data['students']:
        sec = tree.setdefault(st['section'] or '-', OrderedDict())
        for sub in st['subject_wise_results']:
            if sub['is_optional']:
                continue
            node = sec.setdefault(sub['subject'], {
                'appeared': 0, 'failed': 0, 'parts': OrderedDict(), 'total': {'pass_marks': 0, 'dist': defaultdict(int)},
            })
            node['appeared'] += 1
            if sub['status'] != 'fail':
                continue
            node['failed'] += 1
            if sub['failed_parts']:
                for key, label in PART:
                    if key in sub['failed_parts']:
                        p = node['parts'].setdefault(label, {'pass_marks': sub['pass_marks'][key], 'dist': defaultdict(int)})
                        p['dist'][round(sub[f'{key}_marks'] + sub[f'grace_{key}'], 2)] += 1
            else:
                node['total']['pass_marks'] = sub['pass_marks']['total']
                node['total']['dist'][round(sub['total_marks'], 2)] += 1

    def dist_list(d):
        return [{'marks': m, 'students': n} for m, n in sorted(d.items(), key=lambda kv: -kv[0])]

    sections = []
    for sec_name, subs in tree.items():
        subject_rows = []
        for sub_name, n in subs.items():
            parts = [{'part': label, 'pass_marks': n['parts'][label]['pass_marks'],
                      'failed_count': sum(n['parts'][label]['dist'].values()),
                      'distribution': dist_list(n['parts'][label]['dist'])}
                     for _key, label in PART if label in n['parts']]  # সবসময় Written, MCQ, Practical ক্রমে
            total_part = None
            if n['total']['dist']:
                total_part = {'pass_marks': n['total']['pass_marks'], 'failed_count': sum(n['total']['dist'].values()),
                              'distribution': dist_list(n['total']['dist'])}
            subject_rows.append({'subject': sub_name, 'appeared': n['appeared'], 'failed': n['failed'],
                                 'parts': parts, 'total_only': total_part})
        sections.append({'section': sec_name, 'subjects': subject_rows})
    meta = {'class': data['class'], 'section': data['section'], 'total_students': data['total_students']}
    return sections, meta, None


class FailedStudentsView(APIView):
    """
    ফেলের সারাংশ (ছাত্রের নাম ছাড়া): ক্লাস → সেকশন → বিষয় অনুযায়ী, প্রতিটা অংশে (Written/MCQ/Practical)
    কত নম্বর পেয়ে কতজন ফেল। যে অংশে পাস, সেটা ধরা হয় না।
    ?output=pdf দিলে PDF ডাউনলোড, html দিলে প্রিভিউ, না দিলে JSON।
    """
    renderer_classes = [JSONRenderer, BinaryPDFRenderer]
    produces = ['application/pdf', 'application/json']

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('class_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True),
        openapi.Parameter('exam_setup_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True),
        openapi.Parameter('section_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('output', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False,
                          description='json (default) / pdf / html'),
    ])
    def get(self, request):
        import html as _html
        from django.http import HttpResponse
        from django.utils import timezone

        class_id = request.query_params.get('class_id')
        setup_id = request.query_params.get('exam_setup_id')
        if not class_id or not setup_id:
            return Response({'error': 'class_id ও exam_setup_id দিন।'}, status=400)
        sections, meta, err = failed_summary_data(class_id, setup_id, request.query_params.get('section_id'))
        if err is not None:
            return err

        setup = ExamSetup.objects.select_related('exam_name').get(id=setup_id)
        output = request.query_params.get('output', 'json')
        if output not in ('pdf', 'html'):
            return Response({'exam': str(setup), **meta, 'sections': sections}, status=200)

        e = _html.escape

        def dist_text(d):
            return ',  '.join(f"{_fm(x['marks'])} → {x['students']} জন" for x in d)

        body = ''
        for sec in sections:
            body += f"<h3>সেকশন: {e(str(sec['section']))}</h3><table><tr><th>বিষয়</th><th>পরীক্ষা দিয়েছে</th><th>ফেল</th><th>অংশ</th><th>পাস মার্ক</th><th>ফেল</th><th>কত নম্বর পেয়ে কতজন ফেল</th></tr>"
            for s in sec['subjects']:
                lines = [(p['part'], p['pass_marks'], p['failed_count'], p['distribution']) for p in s['parts']]
                if s['total_only']:
                    t = s['total_only']
                    lines.append(('মোট', t['pass_marks'], t['failed_count'], t['distribution']))
                if not lines:
                    body += f"<tr><td class='n'>{e(s['subject'])}</td><td>{s['appeared']}</td><td>0</td><td colspan=4>কেউ ফেল করেনি</td></tr>"
                    continue
                for i, (part, pm, cnt, d) in enumerate(lines):
                    first = (f"<td rowspan={len(lines)} class='n'>{e(s['subject'])}</td><td rowspan={len(lines)}>{s['appeared']}</td>"
                             f"<td rowspan={len(lines)}>{s['failed']}</td>") if i == 0 else ''
                    body += f"<tr>{first}<td>{e(part)}</td><td>{_fm(pm)}</td><td>{cnt}</td><td class='n'>{e(dist_text(d))}</td></tr>"
            body += "</table>"
        font = load_font_base64()
        font_css = ("@font-face{font-family:'SolaimanLipi';src:url(data:font/ttf;base64,%s) format('truetype');}" % font if font else '')
        doc = f"""<!doctype html><html><head><meta charset='utf-8'><style>{font_css}
@page{{size:A4 portrait;margin:10mm}}
body{{font-family:'SolaimanLipi',Arial,sans-serif;font-size:12px;color:#111}}
h1{{text-align:center;margin:0;font-size:20px}} h2{{text-align:center;margin:2px 0 8px;font-size:14px}} h3{{margin:12px 0 4px}}
.meta{{border:1px solid #333;padding:6px 10px;margin-bottom:8px;display:flex;gap:22px;flex-wrap:wrap}}
table{{width:100%;border-collapse:collapse}} th,td{{border:1px solid #444;padding:4px 5px;text-align:center;vertical-align:middle}}
th{{background:#fde8e8}} td.n{{text-align:left}} tr{{page-break-inside:avoid}}
</style></head><body><h1>{e(SCHOOL_NAME)}</h1><h2>ফেলের সারাংশ (বিষয় ও অংশ অনুযায়ী)</h2>
<div class='meta'><div><b>Exam:</b> {e(str(setup))}</div><div><b>Class:</b> {e(str(meta['class']))}</div>
<div><b>Section:</b> {e(str(meta['section']))}</div><div><b>মোট ছাত্র:</b> {meta['total_students']}</div>
<div><b>Printed:</b> {timezone.localtime():%d-%m-%Y %I:%M %p}</div></div>{body}</body></html>"""
        if output == 'html':
            return HttpResponse(doc, content_type='text/html; charset=utf-8')
        resp = HttpResponse(html_to_pdf(doc, landscape=False), content_type='application/pdf')
        resp['Content-Disposition'] = f'attachment; filename="FailedSummary_class{class_id}_setup{setup_id}.pdf"'
        return resp


# ---------------------------------------------------------------------------
# Result প্রকাশের সময় (Admin) ও Public result (সময় হলে নিজে থেকে চালু)
# ---------------------------------------------------------------------------
class ResultPublishScheduleListCreateView(generics.ListCreateAPIView):
    serializer_class = ResultPublishScheduleSerializer

    def get_queryset(self):
        qs = ResultPublishSchedule.objects.select_related('academic_class', 'section', 'exam_setup', 'combined_config')
        for param, field in (('class_id', 'academic_class_id'), ('exam_setup_id', 'exam_setup_id'),
                             ('combined_config_id', 'combined_config_id'), ('section_id', 'section_id')):
            val = self.request.query_params.get(param)
            if val:
                qs = qs.filter(**{field: val})
        return qs


class ResultPublishScheduleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ResultPublishSchedule.objects.select_related('academic_class', 'section', 'exam_setup', 'combined_config')
    serializer_class = ResultPublishScheduleSerializer


class PublicResultView(APIView):
    """
    Public result: Admin এর ঠিক করা সময় পার হলেই চালু, তার আগে 403 (প্রকাশের সময়সহ)।
    একটা exam হলে ওই exam এর result, combined হলে প্রতি exam এর আলাদা নম্বর + যোগ করা result পাশাপাশি।
    ছাত্র বাছতে student_id বা roll_number (সেকশন সহ) দিতে পারো; না দিলে ক্লাস/সেকশনের সবার।
    """
    authentication_classes = []  # মেয়াদ-শেষ token এ 401 এড়াতে
    from rest_framework.permissions import AllowAny as _Allow
    permission_classes = [_Allow]

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('class_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True),
        openapi.Parameter('exam_setup_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('combined_config_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('section_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('student_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
        openapi.Parameter('roll_number', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False),
    ])
    def get(self, request):
        from django.utils import timezone
        from .combined import CombinedResultView

        q = request.query_params
        class_id, setup_id, combined_id = q.get('class_id'), q.get('exam_setup_id'), q.get('combined_config_id')
        section_id = q.get('section_id')
        if not class_id or bool(setup_id) == bool(combined_id):
            return Response({'error': 'class_id এবং exam_setup_id অথবা combined_config_id (একটাই) দিন।'}, status=400)

        schedules = ResultPublishSchedule.objects.filter(academic_class_id=class_id)
        schedules = schedules.filter(exam_setup_id=setup_id) if setup_id else schedules.filter(combined_config_id=combined_id)
        # সেকশন-নির্দিষ্ট সময় থাকলে সেটা, না থাকলে সব সেকশনের সময়
        schedule = None
        if section_id:
            schedule = schedules.filter(section_id=section_id).first()
        schedule = schedule or schedules.filter(section__isnull=True).first()

        if not schedule or not schedule.is_active:
            return Response({'published': False, 'error': 'এই result এখনো প্রকাশের জন্য নির্ধারিত হয়নি।'}, status=403)
        now = timezone.now()
        if schedule.publish_at > now:
            return Response({
                'published': False,
                'publish_at': schedule.publish_at,
                'error': 'এই result এখনো প্রকাশিত হয়নি।',
            }, status=403)

        student_id = q.get('student_id')
        roll = q.get('roll_number')
        if roll and not student_id:
            found = Student.objects.filter(class_name_static_id=class_id, roll_number=roll)
            if section_id:
                found = found.filter(section_static_id=section_id)
            if found.count() != 1:
                return Response({'error': 'রোল দিয়ে একজন ছাত্র নির্দিষ্ট করা যায়নি, section_id ও দিন।'}, status=400)
            student_id = found.first().id

        params = {'class_id': class_id}
        if section_id:
            params['section_id'] = section_id
        if student_id:
            params['student_id'] = student_id
        if setup_id:
            params['exam_setup_id'] = setup_id
            resp = ClassSectionResultSummaryView().get(_Params(params))
        else:
            resp = CombinedResultView().get(_Params(params), combined_id)
        if resp.status_code == 200:
            resp.data = {'published': True, 'publish_at': schedule.publish_at,
                         'is_combined': bool(combined_id), **dict(resp.data)}
        return resp
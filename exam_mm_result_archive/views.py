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
    ExamResultConfig,
    GradeScale,
    StudentExamResult,
    SubjectGroup,
    calculate_grade_and_gpa,
    class_has_practical,
    grade_from_scale,
)
from .serializers import (
    ExamResultConfigSerializer,
    GradeScaleSerializer,
    StudentExamResultSerializer,
    StudentListForResultSerializer,
    BulkResultInputSerializer,
    SubjectGroupSerializer,
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
        self._subject, self._group = {}, {}
        for s in scales:
            target = self._group if s.group_id else self._subject
            key = s.group_id or s.subject_id
            cur = target.get(key)
            if cur is None or (s.academic_class_id and not cur.academic_class_id):
                target[key] = s  # ক্লাস-নির্দিষ্ট তালিকা সাধারণটার ওপরে

    def for_subject(self, subject_id):
        return self._subject.get(subject_id)

    def for_group(self, group_id):
        return self._group.get(group_id)


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
                'written': 0.0, 'mcq': 0.0, 'practical': 0.0, 'grace': 0.0,
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
        cfg = res.result_config
        b['written_pass'] += float(cfg.written_pass_marks)
        b['mcq_pass'] += float(cfg.mcq_pass_marks)
        b['practical_pass'] += float(cfg.practical_pass_marks)
        b['pass_total'] += cfg.total_pass_marks_calc
        b['total'] += float(res.total_marks)
        b['full'] += result_full_marks(res)
    return buckets, skipped


def _evaluate(b, academic_class, scale_book, check_components):
    scale = scale_book.for_group(b['group_id']) if b['group_id'] else scale_book.for_subject(b['subject_id'])
    total, full = b['total'], b['full']
    if scale:
        grade, point = grade_from_scale(scale, total, full)
        source = 'admin'
    else:
        pct = (total / full) * 100 if full > 0 else 0
        grade, point = calculate_grade_and_gpa(pct)
        source = 'default'

    # admin এর দেওয়া মোট pass mark (পেপার যোগ করে) এর নিচে হলে fail
    if b['pass_total'] > 0 and total < b['pass_total']:
        grade, point = 'F', 0.0

    passed = point > 0
    if check_components and class_has_practical(academic_class):
        passed = (
            passed
            and (b['written'] + b['grace']) >= b['written_pass']
            and b['mcq'] >= b['mcq_pass']
            and b['practical'] >= b['practical_pass']
        )

    return {
        'subject': b['name'],
        'papers': sorted(set(b['papers'])) if b['group_id'] else None,
        'is_optional': b['is_optional'],
        'written_marks': round(b['written'], 2),
        'mcq_marks': round(b['mcq'], 2),
        'practical_marks': round(b['practical'], 2),
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
    """
    buckets, skipped = _build_buckets(student, results, group_map)
    rows = [_evaluate(b, academic_class, scale_book, check_components) for b in buckets.values()]

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
            existing_result = None
            if config:
                result = StudentExamResult.objects.filter(
                    student=student,
                    result_config=config
                ).first()
                if result:
                    existing_result = StudentExamResultSerializer(result).data

            student_list.append({
                'id': student.id,
                'full_name': student.full_name,
                'roll_number': student.roll_number,
                'admission_number': student.admission_number,
                'religion': student.religion,
                'existing_result': existing_result,
            })

        return Response({
            'class': academic_class.name,
            'has_practical': class_has_practical(academic_class),
            'result_config': config_data,
            'students': student_list,
        })


class StudentExamResultListCreateView(generics.ListCreateAPIView):
    serializer_class = StudentExamResultSerializer
    pagination_class = ResultPagination
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['student__first_name', 'student__last_name', 'overall_status']

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

            result, is_created = StudentExamResult.objects.update_or_create(
                result_config=config,
                student=student,
                defaults={
                    'written_marks': written,
                    'mcq_marks': mcq,
                    'practical_marks': practical,
                    'section': student.section_static,
                }
            )

            if is_created:
                created.append(student_id)
            else:
                updated.append(student_id)

        return Response({
            'message': f'{len(created)} created, {len(updated)} updated, {len(errors)} errors',
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
    Grace marks একসাথে বসানো (dynamic)। বসানোর পর ওই exam এর সব result নিজে থেকে আবার হিসাব হয়।
    body: { "exam_setup": 5, "grace_marks": 5 }                      → ওই setup এর সব বিষয়ে
          { "exam_setup": 5, "grace_marks": 5, "subject": 21 }       → শুধু একটি বিষয়ে
          { "exam_setup": 5, "grace_marks": 0 }                      → grace তুলে দিতে
    শুধু একটি বিষয়ের জন্য চাইলে result-config/<id>/ এ grace_marks PATCH করলেও হয়।
    """

    @swagger_auto_schema(request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['exam_setup', 'grace_marks'],
        properties={
            'exam_setup': openapi.Schema(type=openapi.TYPE_INTEGER),
            'grace_marks': openapi.Schema(type=openapi.TYPE_NUMBER),
            'subject': openapi.Schema(type=openapi.TYPE_INTEGER, description='ঐচ্ছিক'),
        },
    ))
    def post(self, request):
        setup_id = request.data.get('exam_setup')
        if not setup_id:
            return Response({'error': 'exam_setup দিন।'}, status=400)
        grace, err = to_decimal(request.data.get('grace_marks'), 'Grace marks')
        if err:
            return Response({'error': err}, status=400)
        if grace < 0:
            return Response({'error': 'Grace marks ঋণাত্মক হতে পারবে না।'}, status=400)

        configs = ExamResultConfig.objects.filter(exam_routine__exam_setup_id=setup_id)
        subject_id = request.data.get('subject')
        if subject_id:
            configs = configs.filter(exam_routine__subject_id=subject_id)
        config_ids = list(configs.values_list('id', flat=True))
        if not config_ids:
            return Response({'error': 'এই exam setup এ কোনো result config পাওয়া যায়নি। আগে result-config বানান।'},
                            status=404)

        configs.update(grace_marks=grace)
        count = 0
        for res in StudentExamResult.objects.filter(result_config_id__in=config_ids).select_related(
            'result_config__exam_routine__subject', 'result_config__exam_routine__academic_class'
        ):
            res.save()
            count += 1
        return Response({'configs_updated': len(config_ids), 'results_recalculated': count,
                         'grace_marks': float(grace)})


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


class GradeScaleListCreateView(generics.ListCreateAPIView):
    serializer_class = GradeScaleSerializer
    pagination_class = None

    @swagger_auto_schema(manual_parameters=[
        openapi.Parameter('subject', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        openapi.Parameter('group', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
        openapi.Parameter('academic_class', openapi.IN_QUERY, type=openapi.TYPE_INTEGER),
    ])
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return GradeScale.objects.none()
        qs = GradeScale.objects.select_related('subject', 'group', 'academic_class').prefetch_related('rows')
        p = self.request.query_params
        if p.get('subject'):
            qs = qs.filter(subject_id=p['subject'])
        if p.get('group'):
            qs = qs.filter(group_id=p['group'])
        if p.get('academic_class'):
            qs = qs.filter(academic_class_id=p['academic_class'])
        return qs


class GradeScaleDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GradeScale.objects.select_related('subject', 'group', 'academic_class').prefetch_related('rows')
    serializer_class = GradeScaleSerializer


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
import datetime

from rest_framework import generics, status
from rest_framework.response import Response
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.html import escape
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import ExamsRoutine
from .utils import student_takes_subject, subject_religion
from exam_mm_exam_setup.models import ExamSetup
from apps.students.models import Student
from .serializers import (
    ExamRoutineSerializer,
    ExamRoutineBulkCreateSerializer,
    SingleStudentAdmitCardSerializer,
    ExamRoutineItemForAdmitCardSerializer
)


class ExamRoutineListCreateView(generics.ListCreateAPIView):
    queryset = ExamsRoutine.objects.select_related(
        'exam_name',
        'academic_class',
        'subject',
        'exam_setup'
    ).prefetch_related(
        'exam_setup__sections'
    ).all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ExamRoutineBulkCreateSerializer
        return ExamRoutineSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        setup_id = self.request.query_params.get('exam_setup')
        if setup_id:
            queryset = queryset.filter(exam_setup_id=setup_id)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        created_routines = serializer.save()

        response_serializer = ExamRoutineSerializer(created_routines, many=True)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ExamRoutineDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExamsRoutine.objects.all()
    serializer_class = ExamRoutineSerializer


class ClassWiseAdmitCardGenerateView(generics.GenericAPIView):
    serializer_class = SingleStudentAdmitCardSerializer
    pagination_class = None

    @swagger_auto_schema(
        operation_summary="Generate Admit Cards",
        operation_description="class_id (Required) এবং exam_setup_id অথবা (exam_id + section_id) দিতে হবে। student_id optional।",
        manual_parameters=[
            openapi.Parameter('class_id', openapi.IN_QUERY, description="Academic Class ID (Required)",
                              type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('exam_setup_id', openapi.IN_QUERY, description="Specific Exam Setup ID",
                              type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('exam_id', openapi.IN_QUERY, description="Exam Name ID (section_id সহ দিতে হবে)",
                              type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('section_id', openapi.IN_QUERY, description="Section ID",
                              type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('student_id', openapi.IN_QUERY, description="Optional: specific Student ID",
                              type=openapi.TYPE_INTEGER, required=False),
        ]
    )
    def get(self, request, *args, **kwargs):
        class_id = request.query_params.get('class_id')
        setup_id = request.query_params.get('exam_setup_id')
        exam_id = request.query_params.get('exam_id')
        section_id = request.query_params.get('section_id')
        student_id = request.query_params.get('student_id')

        if not class_id:
            return Response(
                {"error": "'class_id' query parameter is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # 1. Exam Setup (section-specific)
        if setup_id:
            exam_setup = get_object_or_404(ExamSetup, id=setup_id, academic_class_id=class_id)
        elif exam_id and section_id:
            exam_setup = get_object_or_404(
                ExamSetup,
                exam_name_id=exam_id,
                academic_class_id=class_id,
                sections__id=section_id
            )
        else:
            return Response(
                {"error": "'exam_setup_id' অথবা ('exam_id' + 'section_id') দিতে হবে।"},
                status=status.HTTP_400_BAD_REQUEST
            )

        exam_name = exam_setup.exam_name
        academic_class = exam_setup.academic_class

        # 2. শুধু এই setup এর routine
        routines = ExamsRoutine.objects.filter(
            exam_setup=exam_setup
        ).select_related('subject').order_by('exam_date', 'start_time')

        routine_list = list(routines)
        routine_data = ExamRoutineItemForAdmitCardSerializer(routine_list, many=True).data
        routine_pairs = list(zip(routine_list, routine_data))
        has_religion_subject = any(subject_religion(r.subject) for r in routine_list)

        # কোন বিষয় ধর্ম/ঐচ্ছিক হিসেবে ধরা হলো, সেটা দেখানো হয় যাতে ভুল ধরলে বোঝা যায়
        detected_subjects = [
            {
                "subject": r.subject.name,
                "religion": subject_religion(r.subject) or None,
                "is_optional": d["is_optional"],
            }
            for r, d in routine_pairs
            if subject_religion(r.subject) or d["is_optional"]
        ]

        # 3. Students
        students_queryset = Student.objects.filter(class_name_static=academic_class)

        if section_id:
            if not exam_setup.sections.filter(id=section_id).exists():
                return Response(
                    {"error": "এই section এই exam setup এ নেই।"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            students_queryset = students_queryset.filter(section_static_id=section_id)
        else:
            students_queryset = students_queryset.filter(section_static__in=exam_setup.sections.all())

        if student_id:
            students_queryset = students_queryset.filter(id=student_id)

        students = students_queryset.select_related(
            'class_name_static', 'section_static'
        ).order_by('section_static__name', 'roll_number')

        # 4. Response (প্রতিটা ছাত্রের নিজের ধর্ম বিষয় অনুযায়ী routine)
        admit_cards = []
        warnings = []
        for student in students:
            student_info = SingleStudentAdmitCardSerializer(student).data
            student_info['shift'] = exam_setup.shift

            student_routines = [
                data for routine, data in routine_pairs
                if student_takes_subject(student, routine.subject)
            ]

            if has_religion_subject and not any(
                subject_religion(r.subject) and student_takes_subject(student, r.subject)
                for r, _ in routine_pairs
            ):
                warnings.append(
                    f"{student.full_name} (roll {student.roll_number or '-'}): "
                    f"ধর্ম বিষয় পাওয়া যায়নি (প্রোফাইলে ধর্ম: {student.religion or 'দেওয়া নেই'})"
                )

            admit_cards.append({
                "exam_title": exam_name.name,
                "student_info": student_info,
                "routines": student_routines
            })

        return Response({
            "exam_setup_id": exam_setup.id,
            "exam_id": exam_name.id,
            "exam_title": exam_name.name,
            "class_id": academic_class.id,
            "class_name": academic_class.name,
            "total_students": len(admit_cards),
            "detected_subjects": detected_subjects,
            "warnings": warnings,
            "admit_cards": admit_cards
        }, status=status.HTTP_200_OK)


# ---------------------------------------------------------------------------
# Admit Card ছাপা / ডাউনলোড (ব্যাকএন্ডই পুরো কার্ড বানায়)
# ---------------------------------------------------------------------------
SCHOOL_NAME = "Harikhali High School"
HEADMASTER_NAME = "MD. ABDULLAH AL MASUD"


def _fmt_date(value):
    try:
        return datetime.date.fromisoformat(str(value)).strftime('%b %d, %Y').replace(' 0', ' ')
    except ValueError:
        return str(value or '')


def _fmt_time(value):
    try:
        t = datetime.time.fromisoformat(str(value))
    except ValueError:
        return ''
    hour = t.hour % 12 or 12
    return f"{hour}:{t.minute:02d} {'AM' if t.hour < 12 else 'PM'}"


def _fmt_marks(value):
    try:
        number = float(value)
        return str(int(number)) if number == int(number) else f"{number:g}"
    except (TypeError, ValueError):
        return ''


def render_admit_cards_html(data, auto_print=True):
    """admit_cards এর data থেকে ছাপার উপযোগী HTML (প্রতি ছাত্র = ১ পাতা, serial অনুযায়ী)।"""
    cards = []
    for card in data['admit_cards']:
        info = card['student_info']
        rows = []
        for i, r in enumerate(card['routines'], start=1):
            name = escape(r['subject_name']) + (' (4th)' if r.get('is_optional') else '')
            start, end = _fmt_time(r['start_time']), _fmt_time(r['end_time'])
            rows.append(
                f"<tr><td>{i}</td><td>{name}</td><td>{_fmt_date(r['exam_date'])}</td>"
                f"<td>{start} - {end}</td><td class='r'>{_fmt_marks(r['total_marks'])}</td></tr>"
            )
        cards.append(f"""
<section class="card">
  <h1>{escape(SCHOOL_NAME)}</h1>
  <h2>Admit Card</h2>
  <div class="exam">{escape(card['exam_title']).upper()}</div>
  <div class="rule"></div>
  <table class="info">
    <tr><td>Student Name</td><td><b>{escape(info['student_name'])}</b></td></tr>
    <tr><td>Student ID</td><td><b>{escape(str(info['student_id']))}</b></td></tr>
    <tr><td>Roll No</td><td><b>{escape(str(info['roll_no']))}</b></td></tr>
    <tr><td>Class</td><td><b>{escape(info['class_name'])}</b></td></tr>
    <tr><td>Section</td><td><b>{escape(info['section_name'])}</b></td></tr>
    <tr><td>Shift</td><td><b>{escape(str(info.get('shift') or ''))}</b></td></tr>
  </table>
  <div class="sch">EXAM SCHEDULE</div>
  <table class="routine">
    <thead><tr><th>#</th><th>Subject</th><th>Date</th><th>Time</th><th class="r">Marks</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
  <div class="sign">
    <div class="s"><div class="space"></div><div class="line">Student's Signature</div></div>
    <div class="s"><div class="space"></div><div class="line">Class Teacher's Signature</div></div>
    <div class="s">
      <div class="space"><img src="data:image/png;base64,{HEADMASTER_SIGNATURE_B64}" alt=""></div>
      <div class="line"><b>{escape(HEADMASTER_NAME)}</b><br>Head Teacher</div>
    </div>
  </div>
</section>""")

    script = "<script>window.onload=function(){setTimeout(function(){window.print()},500)}</script>" if auto_print else ""
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Admit Cards</title>
<style>
@page {{ size: A4; margin: 14mm; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: "Noto Sans Bengali","Nirmala UI","Kalpurush","SolaimanLipi","Segoe UI",Arial,sans-serif; font-size: 13px; color: #1a1a1a; }}
.card {{ page-break-after: always; break-after: page; padding: 4px 6px; min-height: 255mm; }}
.card:last-child {{ page-break-after: auto; break-after: auto; }}
h1 {{ text-align: center; margin: 0; font-size: 28px; letter-spacing: .3px; }}
h2 {{ text-align: center; margin: 4px 0 0; font-size: 19px; }}
.exam {{ text-align: center; color: #666; font-size: 12px; margin-top: 2px; }}
.rule {{ border-top: 2px solid #4f46e5; margin: 12px 0 14px; }}
table {{ width: 100%; border-collapse: collapse; }}
.info td {{ padding: 6px 8px; border-bottom: 1px solid #eee; }}
.info td:first-child {{ width: 150px; color: #555; }}
.sch {{ margin: 22px 0 8px; color: #4f46e5; font-weight: bold; font-size: 14px; }}
.routine th {{ background: #f4f5f8; text-align: left; padding: 8px; font-size: 12px; border-bottom: 1px solid #ddd; }}
.routine td {{ padding: 8px; border-bottom: 1px solid #eee; }}
.r {{ text-align: right !important; }}
.sign {{ display: flex; gap: 26px; margin-top: 70px; }}
.s {{ flex: 1; text-align: center; }}
.space {{ height: 62px; display: flex; align-items: flex-end; justify-content: center; }}
.space img {{ max-height: 60px; max-width: 100%; }}
.line {{ border-top: 1px solid #333; padding-top: 4px; font-size: 12px; }}
</style></head><body>{''.join(cards)}{script}</body></html>"""


class AdmitCardPrintView(ClassWiseAdmitCardGenerateView):
    """
    class + section + exam দিলে ওই section এর সব ছাত্রের admit card (roll অনুযায়ী serial) একসাথে বানিয়ে দেয়।
    - ডিফল্ট: ছাপার উপযোগী HTML (খুললে নিজে print dialog আসে; "Save as PDF" দিলেই PDF)
    - ?output=pdf : সরাসরি PDF ফাইল ডাউনলোড (সার্ভারে weasyprint ইনস্টল থাকলে)
    - ?print=0 : print dialog ছাড়া শুধু দেখানো
    - ?download=1 : (HTML এর ক্ষেত্রে) ফাইল হিসেবে নামানো
    """

    @swagger_auto_schema(
        operation_summary="Admit Cards ছাপা/ডাউনলোড (HTML বা PDF)",
        manual_parameters=[
            openapi.Parameter('class_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('exam_setup_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('exam_id', openapi.IN_QUERY, description="section_id সহ দিন", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('section_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('student_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('output', openapi.IN_QUERY, description="html (ডিফল্ট) অথবা pdf", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('print', openapi.IN_QUERY, description="0 দিলে print dialog আসবে না", type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('download', openapi.IN_QUERY, description="1 দিলে ফাইল হিসেবে নামবে", type=openapi.TYPE_STRING, required=False),
        ]
    )
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if response.status_code != 200:
            return response
        data = response.data
        if not data['admit_cards']:
            return Response({"error": "এই নির্বাচনে কোনো শিক্ষার্থী পাওয়া যায়নি।"}, status=status.HTTP_404_NOT_FOUND)

        # 'format' নাম DRF নিজে ব্যবহার করে (renderer বাছতে), তাই এখানে 'output'
        fmt = (request.query_params.get('output') or 'html').lower()
        filename = f"admit_cards_{data['class_name']}_{data['exam_title']}".replace(' ', '_')

        if fmt == 'pdf':
            try:
                from weasyprint import HTML
            except Exception:
                return Response(
                    {"error": "PDF বানাতে সার্ভারে weasyprint ইনস্টল নেই। output=html ব্যবহার করুন (print → Save as PDF) অথবা weasyprint ইনস্টল করুন।"},
                    status=status.HTTP_501_NOT_IMPLEMENTED,
                )
            pdf = HTML(string=render_admit_cards_html(data, auto_print=False)).write_pdf()
            out = HttpResponse(pdf, content_type='application/pdf')
            out['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
            return out

        auto_print = request.query_params.get('print', '1') != '0'
        out = HttpResponse(render_admit_cards_html(data, auto_print=auto_print), content_type='text/html; charset=utf-8')
        if request.query_params.get('download') == '1':
            out['Content-Disposition'] = f'attachment; filename="{filename}.html"'
        return out


# প্রধান শিক্ষকের স্বাক্ষর (PNG, base64)। বদলাতে চাইলে এই লাইনের মান বদলান।
HEADMASTER_SIGNATURE_B64 = "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"
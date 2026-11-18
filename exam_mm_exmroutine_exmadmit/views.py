import base64
import datetime
import logging
import os

from django.conf import settings
from rest_framework import generics, status
from rest_framework.renderers import BaseRenderer, JSONRenderer
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


logger = logging.getLogger(__name__)


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
        # student_id URL এর path এ থাকলেও (…/<student_id>/) চলবে, query তেও চলবে
        student_id = kwargs.get('student_id') or request.query_params.get('student_id')

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


# ডাউনলোড করা কপিতে ক্লাস/সেকশনের নাম ইংরেজিতে যাবে (স্ক্রিনের JSON এ বাংলাই থাকে)।
# নতুন কোনো সেকশন/ক্লাস যোগ হলে এখানে এক লাইন যোগ করুন; না পেলে বাংলা নামই ছাপা হবে।
ENGLISH_LABELS = {
    'প্রথম': 'One', 'দ্বিতীয়': 'Two', 'তৃতীয়': 'Three', 'চতুর্থ': 'Four', 'পঞ্চম': 'Five',
    'ষষ্ঠ': 'Six', 'সপ্তম': 'Seven', 'অষ্টম': 'Eight', 'নবম': 'Nine', 'দশম': 'Ten',
    'বকুল': 'Bokul', 'গোলাপ': 'Golap', 'হাসনাহেনা': 'Hasnahena',
    'কোয়েল': 'Koel', 'দোয়েল': 'Doel', 'শালিখ': 'Shalik',
    'পদ্মা': 'Padma', 'যমুনা': 'Jamuna', 'মেঘনা': 'Meghna',
    'বিজ্ঞান': 'Science', 'মানবিক': 'Humanities', 'ব্যবসায় শিক্ষা': 'Business Studies',
    'ফুড প্রসেসিং এন্ড প্রিজার্ভেশন': 'Food Processing and Preservation',
    'এপারেল ম্যানুফেকচারিং বেসিকস': 'Apparel Manufacturing Basics',
}


def _norm_bn(value):
    """বাংলা লেখার একই শব্দ ভিন্ন কোডপয়েন্টে (য় = য+়, ো = ে+া, অদৃশ্য ZWJ) থাকলেও মিলিয়ে নেয়।"""
    import unicodedata
    text = unicodedata.normalize('NFC', str(value or ''))
    text = text.replace('\u200c', '').replace('\u200d', '')
    return ' '.join(text.split())


_ENGLISH_LABELS_NORM = {_norm_bn(k): v for k, v in ENGLISH_LABELS.items()}


def to_english(value):
    text = _norm_bn(value)
    return _ENGLISH_LABELS_NORM.get(text, text)


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


def load_font_base64():
    """Testimonial এর মতোই static/fonts/SolaimanLipi.ttf base64 করে HTML এ বসানো হয়।"""
    font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'SolaimanLipi.ttf')
    if os.path.exists(font_path):
        with open(font_path, 'rb') as font_file:
            return base64.b64encode(font_file.read()).decode('utf-8')
    logger.warning(f"SolaimanLipi font not found at path: {font_path}")
    return ''


def _fit_zoom(routine_count):
    """বিষয় বেশি হলে পুরো কার্ড ছোট করে যেন সবসময় ১ পাতায় ধরে (A4 এর ব্যবহারযোগ্য উচ্চতা ≈ 269mm)।"""
    base_mm, row_mm, usable_mm = 168.0, 9.8, 262.0
    needed = base_mm + row_mm * routine_count
    return round(min(1.0, usable_mm / needed), 3)


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
        zoom = _fit_zoom(len(card['routines']))
        shift = str(info.get('shift') or '').capitalize()
        cards.append(f"""
<section class="card" style="zoom:{zoom}">
  <div class="head">
    <img class="logo" src="data:image/png;base64,{SCHOOL_LOGO_B64}" alt="">
    <h1>{escape(SCHOOL_NAME)}</h1>
  </div>
  <h2>Admit Card</h2>
  <div class="exam">{escape(card['exam_title']).upper()}</div>
  <div class="rule"></div>
  <table class="info">
    <tr><td>Student Name</td><td><b>{escape(info['student_name'])}</b></td></tr>
    <tr><td>Student ID</td><td><b>{escape(str(info['student_id']))}</b></td></tr>
    <tr><td>Roll No</td><td><b>{escape(str(info['roll_no']))}</b></td></tr>
    <tr><td>Class</td><td><b>{escape(to_english(info['class_name']))}</b></td></tr>
    <tr><td>Section</td><td><b>{escape(to_english(info['section_name']))}</b></td></tr>
    <tr><td>Shift</td><td><b>{escape(shift)}</b></td></tr>
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
@font-face {{ font-family: 'SolaimanLipi'; src: url('data:font/truetype;charset=utf-8;base64,{load_font_base64()}') format('truetype'); }}
@page {{ size: A4; margin: 14mm; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: "SolaimanLipi","Nirmala UI","Noto Sans Bengali",Arial,sans-serif; font-size: 13px; color: #1a1a1a; }}
.card {{ page-break-after: always; break-after: page; page-break-inside: avoid; break-inside: avoid; padding: 4px 6px; }}
.card:last-child {{ page-break-after: auto; break-after: auto; }}
.head {{ position: relative; height: 26mm; display: flex; align-items: center; justify-content: center; }}
.logo {{ position: absolute; left: 0; top: 0; height: 26mm; width: auto; }}
h1 {{ margin: 0; font-size: 28px; letter-spacing: .3px; text-align: center; }}
h2 {{ text-align: center; margin: 6px 0 0; font-size: 19px; }}
.exam {{ text-align: center; color: #666; font-size: 12px; margin-top: 2px; }}
.rule {{ border-top: 2px solid #4f46e5; margin: 12px 0 14px; }}
table {{ width: 100%; border-collapse: collapse; }}
.info td {{ padding: 6px 8px; border-bottom: 1px solid #eee; }}
.info td:first-child {{ width: 150px; color: #555; }}
.sch {{ margin: 22px 0 8px; color: #4f46e5; font-weight: bold; font-size: 14px; }}
.routine th {{ background: #f4f5f8; text-align: left; padding: 8px; font-size: 12px; border-bottom: 1px solid #ddd; }}
.routine td {{ padding: 8px; border-bottom: 1px solid #eee; }}
.r {{ text-align: right !important; }}
.sign {{ display: flex; gap: 26px; margin-top: 56px; }}
.s {{ flex: 1; text-align: center; }}
.space {{ height: 62px; display: flex; align-items: flex-end; justify-content: center; }}
.space img {{ max-height: 60px; max-width: 100%; }}
.line {{ border-top: 1px solid #333; padding-top: 4px; font-size: 12px; }}
</style></head><body>{''.join(cards)}{script}</body></html>"""


class BinaryPDFRenderer(BaseRenderer):
    media_type = 'application/pdf'
    format = 'pdf'
    charset = None
    render_style = 'binary'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


class AdmitCardPrintView(ClassWiseAdmitCardGenerateView):
    """
    class + section + exam দিলে ওই section এর সব ছাত্রের admit card (roll অনুযায়ী serial) একসাথে PDF করে নামায়।
    Testimonial এর মতোই Playwright (Chromium) দিয়ে HTML থেকে PDF।
    - ডিফল্ট: PDF ডাউনলোড
    - ?output=html : দেখার জন্য HTML (print=0 দিলে print dialog আসবে না)
    - /<student_id>/ দিলে শুধু একজনের কার্ড
    """
    renderer_classes = [JSONRenderer, BinaryPDFRenderer]
    produces = ['application/pdf']
    # প্রজেক্টের permission AllowAny, তাই লগইন লাগে না। কিন্তু JWTAuthentication থাকলে মেয়াদোত্তীর্ণ/পুরোনো token
    # পাঠালেই 401 দেয় ("Given token not valid for any token type")। প্রিন্ট ডাউনলোডে token যাচাই বন্ধ রাখা হলো।
    authentication_classes = []

    @swagger_auto_schema(
        operation_summary="Admit Cards PDF ডাউনলোড",
        manual_parameters=[
            openapi.Parameter('class_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('exam_setup_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('exam_id', openapi.IN_QUERY, description="section_id সহ দিন", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('section_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('student_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('output', openapi.IN_QUERY, description="pdf (ডিফল্ট) অথবা html", type=openapi.TYPE_STRING, required=False),
        ]
    )
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if response.status_code != 200:
            return response
        data = response.data
        if not data['admit_cards']:
            return Response({"error": "এই নির্বাচনে কোনো শিক্ষার্থী পাওয়া যায়নি।"}, status=status.HTTP_404_NOT_FOUND)

        # 'format' নাম DRF নিজে ব্যবহার করে, তাই এখানে 'output'
        fmt = (request.query_params.get('output') or 'pdf').lower()

        if fmt == 'html':
            auto_print = request.query_params.get('print', '1') != '0'
            return HttpResponse(render_admit_cards_html(data, auto_print=auto_print),
                                content_type='text/html; charset=utf-8')

        from playwright.sync_api import sync_playwright

        html_content = render_admit_cards_html(data, auto_print=False)
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--no-zygote',
                    '--single-process'
                ]
            )
            try:
                context = browser.new_context()
                page = context.new_page()
                page.set_content(html_content, wait_until="load")
                pdf_bytes = page.pdf(
                    format="A4",
                    print_background=True,
                    prefer_css_page_size=True,
                )
            finally:
                browser.close()

        # header এ বাংলা নাম দিলে ভেঙে যায়, তাই শুধু id ব্যবহার
        filename = f"AdmitCards_class{data['class_id']}_setup{data['exam_setup_id']}"
        out = HttpResponse(pdf_bytes, content_type='application/pdf')
        out['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
        out['Access-Control-Expose-Headers'] = 'Content-Disposition'
        return out


# প্রধান শিক্ষকের স্বাক্ষর (PNG, base64)। বদলাতে চাইলে এই লাইনের মান বদলান।
HEADMASTER_SIGNATURE_B64 = "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"

# স্কুলের লোগো (PNG, base64)। বদলাতে চাইলে এই লাইনের মান বদলান।
SCHOOL_LOGO_B64 = "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"






# ---------------------------------------------------------------------------
# Exam Attendance Sheet (তারিখ অনুযায়ী আলাদা শিট, প্রতি পেজে ২৪ জন)
# ---------------------------------------------------------------------------
ATTENDANCE_ROWS_PER_PAGE = 24   # ২০–২৫ এর মধ্যে বদলাতে পারো


def _fmt_date_numeric(value):
    """তারিখ সংখ্যায়: দিন-মাস-বছর (যেমন 17-11-2026)"""
    try:
        return datetime.date.fromisoformat(str(value)).strftime('%d-%m-%Y')
    except ValueError:
        return str(value or '')


def build_attendance_sheets(data):
    """
    admit_cards থেকে (exam_date, section) অনুযায়ী শিট বানায়।
    ধর্ম/ঐচ্ছিক বিষয়ের কারণে সেই তারিখে যার পরীক্ষা নেই, সে ওই শিটে আসবে না।
    """
    sheets = {}
    for card in data['admit_cards']:
        info = card['student_info']
        section = info['section_name']
        for r in card['routines']:
            key = (str(r['exam_date']), section)
            sheet = sheets.setdefault(key, {'subjects': {}, 'students': {}})
            sheet['subjects'][r['subject_name']] = (r['start_time'], r['end_time'])
            sheet['students'].setdefault(info['student_id'], info)  # একজন একবারই
    return [(k, sheets[k]) for k in sorted(sheets)]


def render_attendance_sheets_html(data, auto_print=False):
    pages = []
    for (exam_date, section), sheet in build_attendance_sheets(data):
        students = list(sheet['students'].values())  # আগে থেকেই roll অনুযায়ী সাজানো
        subjects = ', '.join(escape(s) for s in sheet['subjects'])
        times = sorted(set(sheet['subjects'].values()))
        time_text = ' / '.join(f"{_fmt_time(s)} - {_fmt_time(e)}" for s, e in times)
        class_name = escape(to_english(data['class_name']))
        section_name = escape(to_english(section))

        chunks = [students[i:i + ATTENDANCE_ROWS_PER_PAGE]
                  for i in range(0, len(students), ATTENDANCE_ROWS_PER_PAGE)]
        serial = 0
        for page_no, chunk in enumerate(chunks, start=1):
            rows = []
            for st in chunk:
                serial += 1
                rows.append(
                    f"<tr><td class='c'>{serial}</td>"
                    f"<td class='n'>{escape(st['student_name'])}</td>"
                    f"<td class='c'>{escape(str(st['roll_no']))}</td>"
                    f"<td class='c'>{escape(str(st['student_id']))}</td>"
                    f"<td></td><td></td></tr>"
                )
            pages.append(f"""
<section class="page">
  <div class="head">
    <img class="logo" src="data:image/png;base64,{SCHOOL_LOGO_B64}" alt="">
    <h1>{escape(SCHOOL_NAME)}</h1>
  </div>
  <h2>Exam Attendance Sheet</h2>
  <div class="exam">{escape(data['exam_title']).upper()}</div>
  <table class="meta">
    <tr><td>Date: <b>{_fmt_date_numeric(exam_date)}</b></td><td>Subject: <b>{subjects}</b></td><td>Time: <b>{time_text}</b></td></tr>
    <tr><td>Class: <b>{class_name}</b></td><td>Section: <b>{section_name}</b></td>
        <td>Total Students: <b>{len(students)}</b> &nbsp; (Page {page_no}/{len(chunks)})</td></tr>
  </table>
  <table class="list">
    <thead><tr><th style="width:7%">#</th><th style="width:27%">Student Name</th><th style="width:8%">Roll</th>
      <th style="width:14%">Student ID</th><th style="width:22%">Student Signature</th><th style="width:22%">Invigilator Signature</th></tr></thead>
    <tbody>{''.join(rows)}</tbody>
  </table>
</section>""")

    script = "<script>window.onload=function(){setTimeout(function(){window.print()},500)}</script>" if auto_print else ""
    return f"""<!doctype html>
<html><head><meta charset="utf-8"><title>Exam Attendance Sheet</title>
<style>
@font-face {{ font-family: 'SolaimanLipi'; src: url('data:font/truetype;charset=utf-8;base64,{load_font_base64()}') format('truetype'); }}
@page {{ size: A4; margin: 10mm; }}
* {{ box-sizing: border-box; }}
body {{ margin: 0; font-family: "SolaimanLipi","Nirmala UI","Noto Sans Bengali",Arial,sans-serif; font-size: 12px; color: #111; }}
.page {{ page-break-after: always; break-after: page; }}
.page:last-child {{ page-break-after: auto; break-after: auto; }}
.head {{ position: relative; height: 20mm; display: flex; align-items: center; justify-content: center; }}
.logo {{ position: absolute; left: 0; top: 0; height: 20mm; width: auto; }}
h1 {{ margin: 0; font-size: 24px; text-align: center; }}
h2 {{ text-align: center; margin: 3px 0 0; font-size: 16px; }}
.exam {{ text-align: center; font-size: 12px; color: #444; margin: 2px 0 6px; }}
table {{ width: 100%; border-collapse: collapse; }}
.meta td {{ padding: 3px 4px; border: 1px solid #999; font-size: 12px; }}
.list {{ margin-top: 6px; table-layout: fixed; }}
.list th {{ background: #f0f0f0; border: 1px solid #333; padding: 4px; font-size: 11.5px; }}
.list td {{ border: 1px solid #333; height: 8.4mm; padding: 0 4px; overflow: hidden; white-space: nowrap; }}
.list td.n {{ text-align: left; }}
.list td.c {{ text-align: center; }}
</style></head><body>{''.join(pages)}{script}</body></html>"""


class ExamAttendanceSheetPrintView(ClassWiseAdmitCardGenerateView):
    """
    class + section + exam দিলে প্রতিটা পরীক্ষার তারিখের জন্য আলাদা attendance sheet (PDF)।
    প্যারামিটার Admit Card API এর মতোই: class_id, exam_setup_id অথবা (exam_id + section_id)।
    ?output=html দিলে ব্রাউজারে দেখা যাবে।
    """
    renderer_classes = [JSONRenderer, BinaryPDFRenderer]
    produces = ['application/pdf']
    authentication_classes = []

    @swagger_auto_schema(
        operation_summary="Exam Attendance Sheet PDF (তারিখ অনুযায়ী)",
        manual_parameters=[
            openapi.Parameter('class_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=True),
            openapi.Parameter('exam_setup_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('exam_id', openapi.IN_QUERY, description="section_id সহ দিন", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('section_id', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('output', openapi.IN_QUERY, description="pdf (ডিফল্ট) অথবা html", type=openapi.TYPE_STRING, required=False),
        ]
    )
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if response.status_code != 200:
            return response
        data = response.data
        if not data['admit_cards'] or not any(c['routines'] for c in data['admit_cards']):
            return Response({"error": "এই নির্বাচনে কোনো শিক্ষার্থী বা পরীক্ষার routine পাওয়া যায়নি।"},
                            status=status.HTTP_404_NOT_FOUND)

        fmt = (request.query_params.get('output') or 'pdf').lower()
        if fmt == 'html':
            return HttpResponse(render_attendance_sheets_html(data), content_type='text/html; charset=utf-8')

        from playwright.sync_api import sync_playwright

        html_content = render_attendance_sheets_html(data)
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage',
                      '--disable-gpu', '--no-zygote', '--single-process']
            )
            try:
                page = browser.new_context().new_page()
                page.set_content(html_content, wait_until="load")
                pdf_bytes = page.pdf(format="A4", print_background=True, prefer_css_page_size=True)
            finally:
                browser.close()

        filename = f"ExamAttendance_class{data['class_id']}_setup{data['exam_setup_id']}"
        out = HttpResponse(pdf_bytes, content_type='application/pdf')
        out['Content-Disposition'] = f'attachment; filename="{filename}.pdf"'
        out['Access-Control-Expose-Headers'] = 'Content-Disposition'
        return out
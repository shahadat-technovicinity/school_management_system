import os
import base64
import logging
from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.renderers import BaseRenderer
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import IntegerField
from django.db.models.functions import Cast
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from playwright.sync_api import sync_playwright

from apps.students.models import Student
from .models import ExamMark, SubjectPassMarkConfig, GradeScale
from .serializers import (
    StudentInfoFilterSerializer,
    MarkSubmissionSerializer,
    MarksSerializer,
    MarkStatusUpdateSerializer,
    FinalResultSerializer,
    SubjectPassMarkConfigSerializer,
    GradeScaleSerializer,
    convert_eng_to_bng_digits
)

logger = logging.getLogger(__name__)


class StandardLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 100
    max_limit = 500


class BinaryPDFRenderer(BaseRenderer):
    media_type = 'application/pdf'
    format = 'pdf'
    charset = None
    render_style = 'binary'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


# --- Admin Configurations ---
class SubjectPassMarkConfigListCreateAPIView(generics.ListCreateAPIView):
    queryset = SubjectPassMarkConfig.objects.all()
    serializer_class = SubjectPassMarkConfigSerializer
    permission_classes = [AllowAny]


class SubjectPassMarkConfigDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubjectPassMarkConfig.objects.all()
    serializer_class = SubjectPassMarkConfigSerializer
    permission_classes = [AllowAny]


class GradeScaleListCreateAPIView(generics.ListCreateAPIView):
    queryset = GradeScale.objects.all()
    serializer_class = GradeScaleSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, list):
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return super().create(request, *args, **kwargs)


class GradeScaleDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GradeScale.objects.all()
    serializer_class = GradeScaleSerializer
    permission_classes = [AllowAny]


# --- Student Filter ---
class StudentFilterView(generics.ListAPIView):
    serializer_class = StudentInfoFilterSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardLimitOffsetPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('class_name', openapi.IN_QUERY, description="Class ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('section', openapi.IN_QUERY, description="Section ID", type=openapi.TYPE_INTEGER),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Student.objects.none()

        queryset = Student.objects.annotate(
            roll_int=Cast('roll_number', output_field=IntegerField())
        ).order_by('roll_int')

        class_name = self.request.query_params.get('class_name')
        section = self.request.query_params.get('section')

        if class_name and str(class_name).isdigit():
            queryset = queryset.filter(class_name_static_id=int(class_name))
        if section and str(section).isdigit():
            queryset = queryset.filter(section_static_id=int(section))

        return queryset


# --- Marks Submission & Operations ---
class MarksListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MarkSubmissionSerializer
        return MarksSerializer

    def get_queryset(self):
        return ExamMark.objects.filter(status='pending').order_by('-updated_at')

    def create(self, request, *args, **kwargs):
        serializer = MarkSubmissionSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            return Response(result, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MarkRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExamMark.objects.all()
    serializer_class = MarksSerializer
    permission_classes = [AllowAny]


class AdminApprovedMarksListAPIView(generics.ListAPIView):
    serializer_class = MarksSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ExamMark.objects.filter(status='approved').order_by('-updated_at')


class AdminRejectedMarksListAPIView(generics.ListAPIView):
    serializer_class = MarksSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ExamMark.objects.filter(status='rejected').order_by('-updated_at')


class AdminMarkStatusUpdateAPIView(generics.UpdateAPIView):
    queryset = ExamMark.objects.all()
    serializer_class = MarkStatusUpdateSerializer
    permission_classes = [AllowAny]
    http_method_names = ['patch']


# --- Final Results View ---
class FinalResultView(generics.ListAPIView):
    serializer_class = FinalResultSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardLimitOffsetPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('class_name', openapi.IN_QUERY, description="Class ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('section', openapi.IN_QUERY, description="Section ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('exam_type', openapi.IN_QUERY, description="Exam Type Name", type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Student.objects.none()

        queryset = Student.objects.annotate(
            roll_int=Cast('roll_number', output_field=IntegerField())
        ).order_by('roll_int')

        class_name = self.request.query_params.get('class_name')
        section = self.request.query_params.get('section')

        if class_name and str(class_name).isdigit():
            queryset = queryset.filter(class_name_static_id=int(class_name))
        if section and str(section).isdigit():
            queryset = queryset.filter(section_static_id=int(section))

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()

        if getattr(self, "swagger_fake_view", False):
            context['exam_type'] = None
            context['merit_map'] = {}
            return context

        exam_type = self.request.query_params.get('exam_type') if hasattr(self, 'request') else None
        context['exam_type'] = exam_type

        try:
            students = self.get_queryset()
            student_scores = []

            for student in students:
                serializer = FinalResultSerializer(student, context={'request': self.request, 'exam_type': exam_type})
                gpa = serializer.get_gpa(student)
                total_marks = serializer.get_total_marks(student)
                roll = getattr(student, 'roll_int', 999999) or 999999

                student_scores.append({
                    'student_id': student.id,
                    'gpa': gpa,
                    'total_marks': total_marks,
                    'roll': roll
                })

            sorted_students = sorted(
                student_scores,
                key=lambda x: (-x['gpa'], -x['total_marks'], x['roll'])
            )

            merit_map = {item['student_id']: idx + 1 for idx, item in enumerate(sorted_students)}
            context['merit_map'] = merit_map
        except Exception:
            context['merit_map'] = {}

        return context


# --- Playwright PDF Report Download View ---
class DownloadTabulationSheetPDFView(APIView):
    renderer_classes = [BinaryPDFRenderer]
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        class_name = request.query_params.get('class_name')
        exam_type = request.query_params.get('exam_type')

        students = Student.objects.all()
        if class_name and str(class_name).isdigit():
            students = students.filter(class_name_static_id=int(class_name))

        font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'SolaimanLipi.ttf')
        font_base64 = ""
        if os.path.exists(font_path):
            with open(font_path, "rb") as font_file:
                font_base64 = base64.b64encode(font_file.read()).decode('utf-8')

        rows_html = ""
        for idx, student in enumerate(students, 1):
            marks = ExamMark.objects.filter(student=student, status='approved')
            if exam_type:
                marks = marks.filter(exam_type=exam_type)

            total_mark = sum(m.total for m in marks)
            failed_count = marks.filter(is_passed=False).count()
            passed = (failed_count == 0) and marks.exists()
            gpa = round(sum(m.grade_point for m in marks) / marks.count(), 2) if passed and marks.exists() else 0.0

            status_text = "পাস" if passed else f"ফেল ({convert_eng_to_bng_digits(failed_count)} টি বিষয়)"

            rows_html += f"""
            <tr>
                <td>{convert_eng_to_bng_digits(idx)}</td>
                <td>{student.full_name}</td>
                <td>{convert_eng_to_bng_digits(student.roll_number)}</td>
                <td>{convert_eng_to_bng_digits(total_mark)}</td>
                <td>{convert_eng_to_bng_digits(gpa)}</td>
                <td><b style="color: {'green' if passed else 'red'};">{status_text}</b></td>
            </tr>
            """

        html_content = f"""
        <!DOCTYPE html>
        <html lang="bn">
        <head>
            <meta charset="utf-8">
            <style>
                @font-face {{
                    font-family: 'SolaimanLipi';
                    src: url('data:font/truetype;charset=utf-8;base64,{font_base64}') format('truetype');
                }}
                body {{
                    font-family: 'SolaimanLipi', sans-serif;
                    font-size: 11pt;
                    padding: 10px;
                }}
                .title {{
                    text-align: center;
                    font-size: 16pt;
                    font-weight: bold;
                    margin-bottom: 15px;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                }}
                th, td {{
                    border: 1px solid #333;
                    padding: 6px;
                    text-align: center;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
            </style>
        </head>
        <body>
            <div class="title">রেজাল্ট ট্যাবুলেশন শিট</div>
            <table>
                <thead>
                    <tr>
                        <th>ক্র: নং</th>
                        <th>শিক্ষার্থীর নাম</th>
                        <th>রোল নম্বর</th>
                        <th>মোট নম্বর</th>
                        <th>জি.পি.এ (GPA)</th>
                        <th>ফলাফল</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </body>
        </html>
        """

        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage', '--disable-gpu']
            )
            try:
                context = browser.new_context()
                page = context.new_page()
                page.set_content(html_content, wait_until="load")
                pdf_bytes = page.pdf(
                    format="A4",
                    landscape=True,
                    print_background=True,
                    margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"}
                )
            finally:
                browser.close()

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="Tabulation_Sheet.pdf"'
        return response
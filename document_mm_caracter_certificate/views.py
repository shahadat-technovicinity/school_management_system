import os
import base64
import logging
import json as py_json
from datetime import datetime, date

from django.conf import settings
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import BaseRenderer, TemplateHTMLRenderer, JSONRenderer
from playwright.sync_api import sync_playwright

from documment_mm_nothi.models import Nothi
from .models import CharacterCertificateApplication
from .serializers import CharacterCertificateSerializer, CharacterCertificateStatusUpdateSerializer

logger = logging.getLogger(__name__)


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })


def convert_eng_to_bng_digits(text):
    if text is None:
        return ""
    text_str = str(text).strip()
    eng_to_bng_map = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")
    return text_str.translate(eng_to_bng_map)


def format_date_to_bn(date_val):
    if not date_val:
        return ""
    if isinstance(date_val, (datetime, date)):
        raw_str = date_val.strftime("%d/%m/%Y")
    else:
        raw_str = str(date_val).strip()
    return convert_eng_to_bng_digits(raw_str)


class CharacterCertificateListCreateView(generics.ListCreateAPIView):
    queryset = CharacterCertificateApplication.objects.all().order_by('-created_at')
    serializer_class = CharacterCertificateSerializer
    pagination_class = CustomPageNumberPagination


class CharacterCertificateDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CharacterCertificateApplication.objects.all()
    serializer_class = CharacterCertificateSerializer
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'rest_framework/api.html'


class CharacterCertificateStatusUpdateView(generics.UpdateAPIView):
    queryset = CharacterCertificateApplication.objects.all()
    serializer_class = CharacterCertificateStatusUpdateSerializer


class BinaryPDFRenderer(BaseRenderer):
    media_type = 'application/pdf'
    format = 'pdf'
    charset = None
    render_style = 'binary'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


class DownloadCharacterCertificatePDFView(APIView):
    renderer_classes = [BinaryPDFRenderer]
    produces = ['application/pdf']

    def get(self, request, pk, *args, **kwargs):
        try:
            app = CharacterCertificateApplication.objects.get(pk=pk)
        except CharacterCertificateApplication.DoesNotExist:
            return Response({"error": "Character Certificate Application not found"}, status=status.HTTP_404_NOT_FOUND)

        if str(app.status).upper() != 'APPROVED':
            return Response(
                {"error": "This application is not approved yet. Download is restricted."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # Dates & Digits Convert
        serial_no_bn = convert_eng_to_bng_digits(app.serial_no or app.id)
        admission_date_bn = format_date_to_bn(app.admission_date)
        dob_bn = format_date_to_bn(app.date_of_birth)
        
        academic_year_bn = convert_eng_to_bng_digits(app.academic_year)
        passing_year_bn = convert_eng_to_bng_digits(app.passing_year)
        gpa_bn = convert_eng_to_bng_digits(app.gpa)

        # Font Encoding
        font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'SolaimanLipi.ttf')
        font_base64 = ""
        if os.path.exists(font_path):
            with open(font_path, "rb") as font_file:
                font_base64 = base64.b64encode(font_file.read()).decode('utf-8')

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
                    font-size: 14pt;
                    line-height: 2.2;
                    color: #000000;
                    margin: 0;
                    padding: 40px 20px;
                }}
                .title {{
                    text-align: center;
                    font-size: 24pt;
                    font-weight: bold;
                    text-decoration: underline;
                    margin-bottom: 40px;
                }}
                .content {{
                    text-align: justify;
                }}
                .content p {{
                    text-indent: 40px;
                    margin-bottom: 25px;
                }}
                .footer-table {{
                    width: 100%;
                    margin-top: 120px;
                }}
                .footer-table td {{
                    font-weight: bold;
                    font-size: 14pt;
                }}
            </style>
        </head>
        <body>

            <div class="title">চারিত্রিক সনদ পত্র</div>

            <div class="content">
                <p>
                    এই মর্মে প্রত্যয়ন করছি যে, {app.student_name_bn}, পিতা– {app.father_name_bn}, মাতা– {app.mother_name_bn}, গ্রামঃ {app.village}, ডাকঘরঃ {app.post_office}, উপজেলাঃ {app.upazila}, জেলাঃ {app.district}। সে {app.school_name_bn} বিদ্যালয়ে {academic_year_bn} শিক্ষাবর্ষে {admission_date_bn} তারিখে {app.admission_class} শ্রেণিতে ভর্তি হয়ে কৃতিত্বের সাথে শ্রেণি পাঠ্যক্রম সম্পন্ন করে {passing_year_bn} সালে অনুষ্ঠিত এসএসসি পরীক্ষায় অংশগ্রহণ করে {app.exam_group} বিভাগ হতে {gpa_bn} জিপিএ প্রাপ্ত হয়ে উত্তীর্ণ হয়। তার জন্ম তারিখঃ {dob_bn}।
                </p>

                <p>
                    অত্র বিদ্যালয়ে অধ্যয়নকালে সে রাষ্ট্র বিরোধী অথবা নিয়ম শৃঙ্খলা পরিপন্থী কোন কাজে অংশ নেয়নি। তার স্বভাব চরিত্র অতি উত্তম।
                </p>

                <p>
                    আমি তার সর্বাঙ্গীন সাফল্য কামনা করি।
                </p>
            </div>

            <table class="footer-table">
                <tr>
                    <td align="left">প্রস্তুতকারী</td>
                    <td align="right">প্রধান শিক্ষক</td>
                </tr>
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
                    print_background=True,
                    margin={"top": "30mm", "bottom": "25mm", "left": "20mm", "right": "20mm"}
                )
            finally:
                browser.close()

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Character_Certificate_{app.serial_no or app.id}.pdf"'
        response['Access-Control-Expose-Headers'] = 'Content-Disposition'
        return response


class MoveCharacterCertificateToNothiArchiveView(APIView):
    def post(self, request, pk, *args, **kwargs):
        try:
            app = CharacterCertificateApplication.objects.get(pk=pk)
        except CharacterCertificateApplication.DoesNotExist:
            return Response({"error": "Character Certificate Application not found"}, status=status.HTTP_404_NOT_FOUND)

        if app.status.lower() not in ['approved', 'rejected']:
            return Response(
                {"error": "Only Approved or Rejected applications can be moved to Nothi."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        nothi_title = f"Character Certificate Archive ({app.passing_year})"

        nothi_obj, _ = Nothi.objects.get_or_create(
            title=nothi_title,
            defaults={'academic_year': app.passing_year, 'description': '[]'}
        )

        archive_data = {
            "id": app.id,
            "serial_no": app.serial_no,
            "student_name_bn": app.student_name_bn,
            "father_name_bn": app.father_name_bn,
            "mother_name_bn": app.mother_name_bn,
            "passing_year": app.passing_year,
            "gpa": app.gpa,
            "status": app.status,
        }

        try:
            existing_data = py_json.loads(nothi_obj.description) if nothi_obj.description else []
            if not isinstance(existing_data, list):
                existing_data = []
        except Exception:
            existing_data = []

        existing_data.append(archive_data)
        nothi_obj.description = py_json.dumps(existing_data, ensure_ascii=False, indent=2)
        nothi_obj.save()

        app.delete()

        return Response({
            "success": True,
            "message": f"Character Certificate Record archived into Nothi successfully.",
            "nothi_id": nothi_obj.id
        }, status=status.HTTP_200_OK)
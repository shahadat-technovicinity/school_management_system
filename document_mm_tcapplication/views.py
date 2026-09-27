import io
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
from .models import TCApplication
from .serializers import TCApplicationSerializer, TCApplicationStatusUpdateSerializer

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
        raw_str = date_val.strftime("%d-%m-%Y")
    else:
        raw_str = str(date_val).strip()
    return convert_eng_to_bng_digits(raw_str)


class TCApplicationListCreateView(generics.ListCreateAPIView):
    queryset = TCApplication.objects.all().order_by('-created_at')
    serializer_class = TCApplicationSerializer
    pagination_class = CustomPageNumberPagination


class TCApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TCApplication.objects.all()
    serializer_class = TCApplicationSerializer
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'rest_framework/api.html'


class TCApplicationStatusUpdateView(generics.UpdateAPIView):
    queryset = TCApplication.objects.all()
    serializer_class = TCApplicationStatusUpdateSerializer


class BinaryPDFRenderer(BaseRenderer):
    media_type = 'application/pdf'
    format = 'pdf'
    charset = None
    render_style = 'binary'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


class DownloadTCPDFView(APIView):
    renderer_classes = [BinaryPDFRenderer]
    produces = ['application/pdf']

    def get(self, request, pk, *args, **kwargs):
        try:
            application = TCApplication.objects.get(pk=pk)
        except TCApplication.DoesNotExist:
            return Response({"error": "TC Application not found"}, status=status.HTTP_404_NOT_FOUND)

        if str(application.status).upper() != 'APPROVED':
            return Response(
                {"error": "This application is not approved yet. Download is restricted."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # Dates & Digits Convert
        serial_no_bn = convert_eng_to_bng_digits(application.serial_no or application.id)
        issue_date_bn = format_date_to_bn(application.issue_date)
        leaving_date_bn = format_date_to_bn(application.leaving_date)
        dob_bn = format_date_to_bn(application.date_of_birth)
        
        age_years_bn = convert_eng_to_bng_digits(application.age_years)
        age_months_bn = convert_eng_to_bng_digits(application.age_months)
        age_days_bn = convert_eng_to_bng_digits(application.age_days)
        fees_year_bn = convert_eng_to_bng_digits(application.fees_paid_up_to_year)
        reg_no_bn = convert_eng_to_bng_digits(application.registration_no or '---')

        promotion_status = "উত্তীর্ণ হইয়াছে" if application.is_promoted else "উত্তীর্ণ হয় নাই"

        # Font Encoding
        font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'SolaimanLipi.ttf')
        font_base64 = ""
        if os.path.exists(font_path):
            with open(font_path, "rb") as font_file:
                font_base64 = base64.b64encode(font_file.read()).decode('utf-8')

        # HTML Layout matching the attached certificate
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
                    font-size: 13.5pt;
                    line-height: 2.0;
                    color: #000000;
                    margin: 0;
                    padding: 0;
                }}
                .top-meta {{
                    width: 100%;
                    margin-bottom: 20px;
                }}
                .title {{
                    text-align: center;
                    font-size: 20pt;
                    font-weight: bold;
                    margin-bottom: 25px;
                }}
                .content {{
                    text-align: justify;
                }}
                .dotted-line {{
                    border-bottom: 1px dotted #000;
                    display: inline-block;
                    font-weight: bold;
                    padding: 0 5px;
                }}
                .reasons {{
                    margin-top: 15px;
                    margin-left: 20px;
                }}
                .footer-table {{
                    width: 100%;
                    margin-top: 60px;
                }}
                .footer-table td {{
                    text-align: right;
                    font-weight: bold;
                    font-size: 13pt;
                }}
            </style>
        </head>
        <body>
            <table class="top-meta">
                <tr>
                    <td align="left">সিরিয়াল নং- <span class="dotted-line">{serial_no_bn}</span></td>
                    <td align="right">তারিখ: <span class="dotted-line">{issue_date_bn}</span></td>
                </tr>
            </table>

            <div class="title">ছাড়পত্র (মৌলিক)</div>

            <div class="content">
                এই মর্মে প্রত্যয়ন করা যাচ্ছে যে, <span class="dotted-line">{application.student_name_bn}</span><br/>
                পিতা: <span class="dotted-line">{application.father_name_bn}</span> মাতা: <span class="dotted-line">{application.mother_name_bn}</span><br/>
                গ্রাম: <span class="dotted-line">{application.village}</span>, ডাকঘর: <span class="dotted-line">{application.post_office}</span>, উপজেলা: <span class="dotted-line">{application.upazila}</span>, জেলা: <span class="dotted-line">{application.district}</span><br/>
                অত্র বিদ্যালয়ের ছাত্র/ছাত্রী ছিল। সে <span class="dotted-line">{leaving_date_bn}</span> তারিখে উক্ত বিদ্যালয় পরিত্যাগ করিয়াছে। ভর্তি বহির বিবরণ অনুযায়ী তাহার জন্ম তারিখ <span class="dotted-line">{dob_bn}</span>। বিদ্যালয় পরিত্যাগের তারিখে তাহার বয়স ছিল <span class="dotted-line">{age_years_bn}</span> বছর <span class="dotted-line">{age_months_bn}</span> মাস <span class="dotted-line">{age_days_bn}</span> দিন মাত্র।<br/>
                সে <span class="dotted-line">{application.current_class}</span> শ্রেণীতে অধ্যায়ন করিত এবং বিগত বার্ষিক পরীক্ষায় <span class="dotted-line">{application.promoted_from_class}</span> শ্রেণী হইতে <span class="dotted-line">{application.promoted_to_class}</span> শ্রেণীতে <b>{promotion_status}</b>। সে বিদ্যালয়ে বেতন ও অন্যান্য প্রাপ্য টাকা ২০<span class="dotted-line">{fees_year_bn}</span> সাল পর্যন্ত সম্পূর্ণ পরিশোধ করিয়াছে।<br/>
                তাহার রেজিস্ট্রেশন নং: <span class="dotted-line">{reg_no_bn}</span>
                <br/><br/>
                <b>বিদ্যালয় পরিত্যাগের কারণ:</b> <span class="dotted-line">{application.leaving_reason}</span>
            </div>

            <table class="footer-table">
                <tr>
                    <td>
                        প্রধান শিক্ষক<br/>
                        রামরাইল শহীদ ধীরেণ দত্ত উচ্চ বিদ্যালয়
                    </td>
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
                    margin={"top": "50mm", "bottom": "25mm", "left": "18mm", "right": "18mm"}
                )
            finally:
                browser.close()

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="TC_{application.serial_no or application.id}.pdf"'
        response['Access-Control-Expose-Headers'] = 'Content-Disposition'
        return response


class MoveTCToNothiArchiveView(APIView):
    def post(self, request, pk, *args, **kwargs):
        try:
            application = TCApplication.objects.get(pk=pk)
        except TCApplication.DoesNotExist:
            return Response({"error": "TC Application not found"}, status=status.HTTP_404_NOT_FOUND)

        if application.status.lower() not in ['approved', 'rejected']:
            return Response(
                {"error": "Only Approved or Rejected applications can be moved to Nothi."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        nothi_title = f"TC Archive ({application.fees_paid_up_to_year})"

        nothi_obj, _ = Nothi.objects.get_or_create(
            title=nothi_title,
            defaults={'academic_year': application.fees_paid_up_to_year, 'description': '[]'}
        )

        tc_data = {
            "id": application.id,
            "serial_no": application.serial_no,
            "student_name_bn": application.student_name_bn,
            "father_name_bn": application.father_name_bn,
            "mother_name_bn": application.mother_name_bn,
            "leaving_date": str(application.leaving_date),
            "leaving_reason": application.leaving_reason,
            "status": application.status,
        }

        try:
            existing_data = py_json.loads(nothi_obj.description) if nothi_obj.description else []
            if not isinstance(existing_data, list):
                existing_data = []
        except Exception:
            existing_data = []

        existing_data.append(tc_data)
        nothi_obj.description = py_json.dumps(existing_data, ensure_ascii=False, indent=2)
        nothi_obj.save()

        application.delete()

        return Response({
            "success": True,
            "message": f"TC Record archived into Nothi successfully.",
            "nothi_id": nothi_obj.id
        }, status=status.HTTP_200_OK)
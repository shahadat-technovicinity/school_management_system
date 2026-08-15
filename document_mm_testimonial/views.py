import io
import os
import base64
import qrcode

from django.http import HttpResponse
from django.conf import settings
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import BaseRenderer
from playwright.sync_api import sync_playwright

from .models import StudentApplication
from .serializers import StudentApplicationSerializer, StudentApplicationStatusUpdateSerializer


class StudentApplicationListCreateView(generics.ListCreateAPIView):
    queryset = StudentApplication.objects.all().order_by('-created_at')
    serializer_class = StudentApplicationSerializer
    pagination_class = PageNumberPagination


class StudentApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentApplication.objects.all()
    serializer_class = StudentApplicationSerializer


class StudentApplicationStatusUpdateView(generics.UpdateAPIView):
    queryset = StudentApplication.objects.all()
    serializer_class = StudentApplicationStatusUpdateSerializer


class BinaryPDFRenderer(BaseRenderer):
    media_type = 'application/pdf'
    format = 'pdf'
    charset = None
    render_style = 'binary'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return data


class DownloadTestimonialPDFView(APIView):
    renderer_classes = [BinaryPDFRenderer]

    def get(self, request, pk, *args, **kwargs):
        try:
            application = StudentApplication.objects.get(pk=pk)
        except StudentApplication.DoesNotExist:
            return Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)

        # 1. Available Font Encoding (SolaimanLipi)
        font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'SolaimanLipi.ttf')
        font_base64 = ""
        if os.path.exists(font_path):
            with open(font_path, "rb") as font_file:
                font_base64 = base64.b64encode(font_file.read()).decode('utf-8')

        # 2. Dynamic Verification QR Code (Base64)
        base_url = "https://api.harikhalihs.edu.bd"
        verify_url = f"{base_url}/document_mm_testimonial/applications/{application.id}/"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=4,
            border=1,
        )
        qr.add_data(verify_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        qr_b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        qr_image_data = f"data:image/png;base64,{qr_b64}"
        buffer.close()

        # 3. HTML Layout Structure
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
                    line-height: 1.8;
                    color: #000000;
                    margin: 0;
                    padding: 40pt;
                }}
                .app-id {{
                    font-family: Arial, sans-serif;
                    font-size: 11pt;
                    color: #333333;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .title {{
                    text-align: center;
                    font-size: 24pt;
                    font-weight: bold;
                    margin-bottom: 30px;
                    text-decoration: underline;
                }}
                .content {{
                    text-align: justify;
                    margin-bottom: 40px;
                }}
                .footer-table {{
                    width: 100%;
                    margin-top: 60px;
                    border-collapse: collapse;
                }}
                .footer-table td {{
                    text-align: center;
                    vertical-align: bottom;
                    font-weight: bold;
                    font-size: 13pt;
                }}
                .qr-code {{
                    width: 75px;
                    height: 75px;
                }}
            </style>
        </head>
        <body>
            <div class="app-id">ID: {application.id}</div>
            <div class="title">প্রশংসা পত্র</div>
            
            <div class="content">
                এই মর্মে প্রশংসা পত্র প্রদান করিতেছি যে, <b>{application.student_name_bn}</b>, 
                পিতা: <b>{application.father_name_bn}</b>, মাতা: <b>{application.mother_name_bn}</b>, 
                গ্রাম: <b>{application.village}</b>, ডাকঘর: <b>{application.post_office}</b>, 
                উপজেলা: <b>{application.upazila}</b>, জেলা: <b>{application.district}</b>। 
                সে অত্র হরিখালী উচ্চ বিদ্যালয়ের দশম শ্রেণির শিক্ষার্থী ছিল। 
                সে <b>{application.passing_year}</b> সালের <b>{application.exam_month}</b> মাসে 
                <b>{application.board}</b> কর্তৃক অনুষ্ঠিত সেকেন্ডারী স্কুল সার্টিফিকেট পরীক্ষায় 
                <b>{application.department}</b> বিভাগে অংশ গ্রহণ করিয়া <b>{application.grade}</b> গ্রেডে উত্তীর্ণ হইয়াছে। 
                তাহার গ্রেড পয়েন্ট এভারেজ(GPA) <b>{application.gpa}</b>, তাহার পরীক্ষার রোল সোনার নং <b>{application.roll}</b>, 
                নিবন্ধন সংখ্যা <b>{application.registration_no}</b>, শিক্ষাবর্ষ <b>{application.academic_year}</b>। 
                তাহার জন্ম তারিখ <b>{application.date_of_birth}</b>।
                <br/><br/>
                যতদূর জানি তাহার স্বভাব চরিত্র ভালো এবং অত্র বিদ্যালয়ে অধ্যয়নকালে সে রাষ্ট্র বিরোধী অথবা নিয়ম শৃঙ্খলা পরিপন্থী কোন কাজে অংশ গ্রহণ করে নাই।
                <br/><br/>
                আমি তাহার সাফল্য কামনা করি।
            </div>

            <table class="footer-table">
                <tr>
                    <td width="35%">অফিস সহকারী</td>
                    <td width="30%">
                        <img src="{qr_image_data}" class="qr-code" alt="QR Code" />
                    </td>
                    <td width="35%">প্রধান শিক্ষক</td>
                </tr>
            </table>
        </body>
        </html>
        """

        # 4. Safe PDF Generation with Crash Prevention Arguments
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu'
                ]
            )
            try:
                context = browser.new_context()
                page = context.new_page()
                page.set_content(html_content, wait_until="networkidle")
                
                pdf_bytes = page.pdf(
                    format="A4",
                    print_background=True,
                    margin={"top": "15mm", "bottom": "15mm", "left": "15mm", "right": "15mm"}
                )
            finally:
                browser.close()

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Testimonial_{application.roll}.pdf"'
        return response
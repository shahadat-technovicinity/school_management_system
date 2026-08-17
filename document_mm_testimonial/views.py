import io
import os
import base64
import qrcode
from datetime import datetime, date

from django.http import HttpResponse
from django.conf import settings
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.renderers import BaseRenderer, TemplateHTMLRenderer, JSONRenderer
from playwright.sync_api import sync_playwright

from .models import StudentApplication
from .serializers import StudentApplicationSerializer, StudentApplicationStatusUpdateSerializer


def convert_eng_to_bng_digits(text):
    """ইংরেজি ডিজিট, সংখ্যা বা None-কে নিরাপদে বাংলা ডিজিটে রূপান্তর করার হেলপার ফাংশন"""
    if text is None:
        return ""
    text_str = str(text).strip()
    eng_to_bng_map = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")
    return text_str.translate(eng_to_bng_map)


class StudentApplicationListCreateView(generics.ListCreateAPIView):
    queryset = StudentApplication.objects.all().order_by('-created_at')
    serializer_class = StudentApplicationSerializer
    pagination_class = PageNumberPagination


class StudentApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentApplication.objects.all()
    serializer_class = StudentApplicationSerializer
    renderer_classes = [TemplateHTMLRenderer, JSONRenderer]
    template_name = 'rest_framework/api.html'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        return response


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
    produces = ['application/pdf']

    def get(self, request, pk, *args, **kwargs):
        try:
            application = StudentApplication.objects.get(pk=pk)
        except StudentApplication.DoesNotExist:
            return Response({"error": "Application not found"}, status=status.HTTP_404_NOT_FOUND)

        # -------------------------------------------------------------
        # 0. Status Check: Approve না থাকলে ডাউনলোড ব্লক করবে
        # -------------------------------------------------------------
        # আপনার মডেলের স্ট্যাটাস ফিল্ডের মান অনুযায়ী 'APPROVED' বা 'approved' ব্যবহার করুন
        if str(application.status).upper() != 'APPROVED':
            return Response(
                {"error": "This application is not approved yet. Download is restricted."}, 
                status=status.HTTP_403_FORBIDDEN
            )

        # 1. Safe Date Formatting (Handles string, datetime, and date objects)
        formatted_dob = ""
        if application.date_of_birth:
            dob_val = application.date_of_birth
            if isinstance(dob_val, (datetime, date)):
                raw_dob_str = dob_val.strftime("%d-%m-%Y")
            else:
                raw_dob_str = str(dob_val).strip()
                try:
                    dob_obj = datetime.strptime(raw_dob_str, "%Y-%m-%d")
                    raw_dob_str = dob_obj.strftime("%d-%m-%Y")
                except ValueError:
                    try:
                        dob_obj = datetime.strptime(raw_dob_str, "%d-%m-%Y")
                        raw_dob_str = dob_obj.strftime("%d-%m-%Y")
                    except ValueError:
                        pass

            formatted_dob = convert_eng_to_bng_digits(raw_dob_str)

        # 2. Safe Field Conversions
        passing_year_bn = convert_eng_to_bng_digits(application.passing_year)
        roll_bn = convert_eng_to_bng_digits(application.roll)
        registration_no_bn = convert_eng_to_bng_digits(application.registration_no)
        gpa_bn = convert_eng_to_bng_digits(application.GPA)
        academic_year_bn = convert_eng_to_bng_digits(application.academic_year)
        app_id_bn = convert_eng_to_bng_digits(application.id)

        # 3. Font Encoding
        font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'SolaimanLipi.ttf')
        font_base64 = ""
        if os.path.exists(font_path):
            with open(font_path, "rb") as font_file:
                font_base64 = base64.b64encode(font_file.read()).decode('utf-8')

        # 4. Dynamic Verification QR Code
        base_url = "https://api.harikhalihs.edu.bd"
        verify_url = f"{base_url}/document_mm_testimonial/applications/{application.id}/?format=html"
        
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

        # 5. Corrected HTML Layout Structure for Pad Printing
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
                    line-height: 1.8;
                    color: #000000;
                    margin: 0;
                    padding: 0;
                    letter-spacing: normal;
                    word-spacing: normal;
                }}
                .header-meta {{
                    width: 100%;
                    margin-bottom: 15px;
                }}
                .app-id {{
                    font-family: Arial, sans-serif;
                    font-size: 10.5pt;
                    color: #333333;
                    font-weight: bold;
                }}
                .title {{
                    text-align: center;
                    font-size: 22pt;
                    font-weight: bold;
                    margin-top: 10px;
                    margin-bottom: 25px;
                    text-decoration: underline;
                }}
                .content {{
                    text-align: justify;
                    margin-bottom: 30px;
                }}
                .footer-table {{
                    width: 100%;
                    margin-top: 40px;
                    border-collapse: collapse;
                }}
                .footer-table td {{
                    text-align: center;
                    vertical-align: bottom;
                    font-weight: bold;
                    font-size: 12.5pt;
                }}
                .qr-code {{
                    width: 70px;
                    height: 70px;
                }}
            </style>
        </head>
        <body>
            <div class="header-meta">
                <span class="app-id">ID: {application.id}</span>
            </div>
            
            <div class="title">প্রশংসাপত্র</div>
            
            <div class="content">
                এই মর্মে প্রশংসাপত্র প্রদান করছি যে, <b>{application.student_name_bn or ''}</b>, 
                পিতা: <b>{application.father_name_bn or ''}</b>, মাতা: <b>{application.mother_name_bn or ''}</b>, 
                গ্রাম: <b>{application.village or ''}</b>, ডাকঘর: <b>{application.post_office or ''}</b>, 
                উপজেলা: <b>{application.upazila or ''}</b>, জেলা: <b>{application.district or ''}</b>। 
                সে অত্র হরিখালী উচ্চ বিদ্যালয় থেকে <b>{passing_year_bn}</b> সালের 
                <b>{application.exam_month or ''}</b> মাসে <b>{application.board or ''}</b> কর্তৃক অনুষ্ঠিত সেকেন্ডারী স্কুল সার্টিফিকেট পরীক্ষায় 
                <b>{application.department or ''}</b> বিভাগে অংশগ্রহণ করে <b>{application.grade or ''}</b> লেটার গ্রেডে উত্তীর্ণ হয়েছে। 
                তার প্রাপ্ত গ্রেড পয়েন্ট এভারেজ(GPA) <b>{gpa_bn}</b>, তার পরীক্ষার রোল নং <b>{roll_bn}</b>, 
                রেজিস্ট্রেশন নং <b>{registration_no_bn}</b>, শিক্ষাবর্ষ <b>{academic_year_bn}</b> এবং 
                তার জন্ম তারিখ <b>{formatted_dob}</b>।
                <br/><br/>
                যতদূর জানি তার স্বভাব-চরিত্র ভালো এবং অত্র বিদ্যালয়ে অধ্যয়নকালে সে কোনো রাষ্ট্র বিরোধী অথবা নিয়ম-শৃঙ্খলা পরিপন্থী কোন কাজে অংশগ্রহণ করে নাই।
                <br/><br/>
                আমি তার সাফল্য কামনা করি।
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

        # 6. Playwright PDF Generation
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
                    margin={
                        "top": "60mm",
                        "bottom": "30mm",
                        "left": "18mm",
                        "right": "18mm"
                    }
                )
            finally:
                browser.close()

        response = HttpResponse(pdf_bytes, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Testimonial_{application.roll}.pdf"'
        response['Access-Control-Expose-Headers'] = 'Content-Disposition'
        return response
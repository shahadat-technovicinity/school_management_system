from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.students.models import Student
from .models import SMSTemplate, SMSHistory
from .serializers import SMSTemplateSerializer, SMSHistorySerializer
from .sms import send_sms_net_bd, check_sms_balance


class SendFlexibleSMSView(APIView):
    """
    একক, bulk, ম্যানুয়াল অথবা Class/Section ভিত্তিক স্টুডেন্টদের অভিভাবকদের SMS পাঠানোর ভিউ।
    """
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'class_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="Class Filter ID (Optional)"),
                'section_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="Section Filter ID (Optional)"),
                'manual_numbers': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description="Manual phone numbers list ['01700000000'] (Optional)"
                ),
                'template_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="Database SMSTemplate ID (Optional)"),
                'message': openapi.Schema(type=openapi.TYPE_STRING, description="Custom Message Content (Optional)"),
                'content_id': openapi.Schema(type=openapi.TYPE_STRING, description="sms.net.bd Content ID (Optional)"),
                'schedule': openapi.Schema(type=openapi.TYPE_STRING, description="Schedule time: Y-m-d H:i:s (Optional)"),
            }
        )
    )
    def post(self, request, *args, **kwargs):
        class_id = request.data.get('class_id')
        section_id = request.data.get('section_id')
        manual_numbers = request.data.get('manual_numbers', [])
        template_id = request.data.get('template_id')
        custom_message = request.data.get('message')
        content_id = request.data.get('content_id')
        schedule = request.data.get('schedule')

        final_message = custom_message
        final_content_id = content_id

        # ১. টেমপ্লেট সেটিং এবং ভ্যালিডেশন
        if template_id:
            try:
                sms_template = SMSTemplate.objects.get(id=template_id)
                # কাস্টম মেসেজ না থাকলে টেমপ্লেটের বডি সরাসরি ব্যবহার করবে
                if not final_message:
                    final_message = sms_template.message_body
                if sms_template.content_id and not final_content_id:
                    final_content_id = sms_template.content_id
            except SMSTemplate.DoesNotExist:
                # কাস্টম মেসেজ বা কনটেন্ট আইডি না থাকলে তবেই ৪০৪ এরর দিবে
                if not final_message and not final_content_id:
                    return Response(
                        {"error": f"ID {template_id} এর কোনো SMS টেমপ্লেট ডাটাবেজে পাওয়া যায়নি।"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )

        if not final_message and not final_content_id:
            return Response(
                {"error": "মেসেজ পাঠানোর জন্য 'message', 'template_id' অথবা 'content_id' প্রদান করুন।"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        target_contacts = []
        phone_numbers_set = set()

        # ২. Class & Section ভিত্তিক স্টুডেন্ট ফিল্টারিং
        if class_id or section_id:
            queryset = Student.objects.filter(status="active").select_related('guardian_info')

            if class_id:
                queryset = queryset.filter(class_name_static_id=class_id)
            if section_id:
                queryset = queryset.filter(section_static_id=section_id)

            for student in queryset:
                guardian = getattr(student, 'guardian_info', None)
                if guardian:
                    # guardian_phone না থাকলে father_phone ব্যবহার করবে
                    phone = getattr(guardian, 'guardian_phone', None) or getattr(guardian, 'father_phone', None)
                    if phone and str(phone).strip():
                        clean_phone = str(phone).strip()
                        target_contacts.append((student, clean_phone))
                        phone_numbers_set.add(clean_phone)

        # ৩. ম্যানুয়াল ফোন নম্বর হ্যান্ডলিং
        if manual_numbers and isinstance(manual_numbers, list):
            for raw_num in manual_numbers:
                if raw_num and str(raw_num).strip():
                    clean_num = str(raw_num).strip()
                    if clean_num not in phone_numbers_set:
                        target_contacts.append((None, clean_num))
                        phone_numbers_set.add(clean_num)

        if not target_contacts:
            return Response(
                {"error": "কোনো বৈধ প্রাপকের ফোন নম্বর পাওয়া যায়নি। নির্বাচিত Class/Section-এ সক্রিয় স্টুডেন্ট বা অভিভাবকের নম্বর আছে কিনা চেক করুন।"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # ৪. SMS Gateway (sms.net.bd) কল করা
        success, api_response = send_sms_net_bd(
            recipients=list(phone_numbers_set),
            message=final_message,
            content_id=final_content_id,
            schedule=schedule
        )

        request_id = None
        error_msg = None

        if success:
            req_status = 'SUCCESS'
            request_id = str(api_response.get('data', {}).get('request_id', ''))
        else:
            req_status = 'FAILED'
            error_msg = str(api_response.get('msg', 'SMS Delivery Failed'))

        # ৫. বাল্ক হিস্ট্রি রেকর্ড তৈরি
        history_records = [
            SMSHistory(
                student=student_obj,
                phone_number=phone,
                message=final_message or f"Content ID: {final_content_id}",
                request_id=request_id,
                status=req_status,
                error_message=error_msg
            )
            for student_obj, phone in target_contacts
        ]

        SMSHistory.objects.bulk_create(history_records)

        if success:
            return Response({
                "status": "Success",
                "message": "এসএমএস সফলভাবে পাঠানো হয়েছে।",
                "total_recipients": len(target_contacts),
                "api_response": api_response
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "Failed",
                "message": "এসএমএস পাঠাতে ব্যর্থ হয়েছে।",
                "api_response": api_response
            }, status=status.HTTP_400_BAD_REQUEST)


class SMSTemplateListCreateView(ListCreateAPIView):
    """ টেমপ্লেট তৈরি এবং তালিকা দেখার জন্য API """
    queryset = SMSTemplate.objects.all()
    serializer_class = SMSTemplateSerializer


class SMSTemplateDetailView(RetrieveUpdateDestroyAPIView):
    """ নির্দিষ্ট টেমপ্লেট দেখা, এডিট বা ডিলিট করার জন্য API """
    queryset = SMSTemplate.objects.all()
    serializer_class = SMSTemplateSerializer


class SMSHistoryListView(ListAPIView):
    """ পাঠানো SMS-এর ইতিহাস (History) দেখার API """
    serializer_class = SMSHistorySerializer

    def get_queryset(self):
        queryset = SMSHistory.objects.select_related('student').all()
        student_id = self.request.query_params.get('student_id')
        status_param = self.request.query_params.get('status')

        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if status_param:
            queryset = queryset.filter(status=status_param.upper())

        return queryset


class CheckSMSBalanceView(APIView):
    """ Gateway-এর বর্তমান SMS ব্যালেন্স চেক করার API """
    def get(self, request, *args, **kwargs):
        balance_info = check_sms_balance()
        return Response(balance_info, status=status.HTTP_200_OK)



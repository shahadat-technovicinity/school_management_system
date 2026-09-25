from rest_framework import generics
from .models import *
from .serializers import *
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from drf_yasg.utils import swagger_auto_schema
import re

# App Models
from apps.students.models import Student
from academic_mm_class_and_section.models import AcademicClass, Section
from apps.staff.models import StaffProfile
from teacher_mm_teacher.models import TeacherAndStaffProfile
from .serializers import SchoolDashboardStatsSerializer



class Home_Page_SliderListCreateView(generics.ListCreateAPIView):
    queryset = Home_Page_Slider.objects.all()
    serializer_class = Home_Page_SliderSerializer
    parser_classes = (MultiPartParser, FormParser)

class Home_Page_SliderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Home_Page_Slider.objects.all()
    serializer_class = Home_Page_SliderSerializer
    lookup_field = 'pk' 
    parser_classes = (MultiPartParser, FormParser)



#### Message Views
class MessageListCreateView(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

# Detail, Update, Delete View
class MessageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer



## Admission Notice Views
class AdmissionNoticeListCreateView(generics.ListCreateAPIView):
    queryset = AdmissionNotice.objects.all()
    serializer_class = AdmissionNoticeSerializer


class AdmissionNoticeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AdmissionNotice.objects.all()
    serializer_class = AdmissionNoticeSerializer
    lookup_field = 'pk'




# Contact Message Views
class ContactMessageListCreateView(generics.ListCreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer


class ContactMessageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    lookup_field = 'pk'



# Letter Info Views
class LetterInfoListCreateView(generics.ListCreateAPIView):
    queryset = LetterInfo.objects.all()
    serializer_class = LatterSerializer
    parser_classes = (MultiPartParser, FormParser)


class LetterInfoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LetterInfo.objects.all()
    serializer_class = LatterSerializer
    lookup_field = 'pk'
    parser_classes = (MultiPartParser, FormParser)




# Student & teacher staff count view for school dashboard

class SchoolDashboardStatsAPIView(APIView):
    """
    Dynamic analytics API for homepage and dashboard overview.
    """

    @swagger_auto_schema(
        responses={200: SchoolDashboardStatsSerializer()},
        operation_description="Returns real-time counts for students, teachers, staff, and class-wise student stats."
    )
    def get(self, request, *args, **kwargs):
        # কারেন্ট একাডেমিক ইয়ার বের করা (যেমন: "2026")
        current_year = str(timezone.now().year)

        # ১. রানিং ইয়ারের অ্যাক্টিভ স্টুডেন্ট ফিল্টার
        active_students_qs = Student.objects.filter(
            status="active",
            academic_year__icontains=current_year
        )

        total_students_count = active_students_qs.count()

        # Active Teachers count
        total_teachers_count = TeacherAndStaffProfile.objects.filter(
            employee_type="teacher", 
            status="active"
        ).count()

        # Active Staff count
        total_staff_count = TeacherAndStaffProfile.objects.filter(
            employee_type="staff", 
            status="active"
        ).count()

        # ২. Dynamic summary response formatting
        summary_data = {
            "total_students_summary": f"{total_students_count}+",
            "total_teachers_summary": f"{total_teachers_count}+",
            "total_staff_summary": f"{total_staff_count}+",
        }

        # ৩. Dynamic class-wise student counts (Class ID এবং Name সহ Query)
        class_wise_qs = (
            active_students_qs
            .exclude(class_name_static__isnull=True)
            .values('class_name_static__id', 'class_name_static__name')
            .annotate(total_students=Count('id'))
            .order_by('class_name_static__id')  # ID বা মডেলের ডিফল্ট সিকোয়েন্স অনুযায়ী ডাটাবেজ থেকেই সর্ট হবে
        )

        # বাংলা শব্দের জন্য কাস্টম ম্যাপ (যদি ID অনুযায়ী অর্ডার না হয় তবে ফালব্যাক হিসেবে কাজ করবে)
        class_order_map = {
            "ষষ্ঠ": 1,
            "সপ্তম": 2,
            "অষ্টম": 3,
            "নবম": 4,
            "দশম": 5,
        }

        class_wise_students = []
        for item in class_wise_qs:
            c_name = item['class_name_static__name'] if item['class_name_static__name'] else "N/A"
            
            # সর্টিং কী নির্ধারণ (প্রথমত ID, দ্বিতীয়ত বাংলা নাম ম্যাপ, না মিললে Regex, নতুবা 999)
            c_id = item['class_name_static__id'] or 999
            
            class_wise_students.append({
                "class_id": c_id,
                "class_name": c_name,
                "total_students": item['total_students']
            })

        # ৪. নিখুঁত সর্টিং: Class ID -> বাংলা ম্যাপ -> ইংরেজি ডিজিট
        def get_sort_key(item):
            name = str(item['class_name']).strip()
            # ১. যদি বাংলা ম্যাপে থাকে
            if name in class_order_map:
                return class_order_map[name]
            # ২. যদি নামের মধ্যে ডিজিট থাকে (যেমন Class 6 বা ৬)
            digit_match = re.search(r'\d+', name)
            if digit_match:
                return int(digit_match.group())
            # ৩. অন্যথায় Class ID ব্যবহার করবে
            return item['class_id']

        class_wise_students = sorted(class_wise_students, key=get_sort_key)

        # Serializer-এর ফরম্যাট অনুযায়ী class_id রিমুভ করে ক্লিন লিস্ট প্রস্তুত
        formatted_class_wise = [
            {
                "class_name": item["class_name"],
                "total_students": item["total_students"]
            }
            for item in class_wise_students
        ]

        response_payload = {
            **summary_data,
            "class_wise_students": formatted_class_wise
        }

        serializer = SchoolDashboardStatsSerializer(data=response_payload)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
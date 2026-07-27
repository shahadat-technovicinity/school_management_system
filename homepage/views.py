from rest_framework import generics
from .models import *
from .serializers import *
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from drf_yasg.utils import swagger_auto_schema

# App Models
from apps.students.models import Student
from apps.academics.models import Class
from apps.staff.models import StaffProfile
from teacher_mm_teacher.models import Teacher  # Teacher model from teacher_mm_teacher app

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
        # 1. Real-time database counts
        total_students_count = Student.objects.filter(status="active").count()
        
        # Teacher count filter
        total_teachers_count = Teacher.objects.filter(status="active").count() if hasattr(Teacher, 'status') else Teacher.objects.count()
        
        # Staff count filter
        total_staff_count = StaffProfile.objects.filter(status="active").count() if hasattr(StaffProfile, 'status') else StaffProfile.objects.count()

        # 2. Dynamic summary response formatting
        summary_data = {
            "total_students_summary": f"{total_students_count}+",
            "total_teachers_summary": f"{total_teachers_count}+",
            "total_staff_summary": f"{total_staff_count}+",
        }

        # 3. Dynamic class-wise student counts directly from Student model
        class_wise_qs = (
            Student.objects.filter(status="active")
            .exclude(class_name_static__isnull=True)
            .exclude(class_name_static__exact="")
            .values('class_name_static')
            .annotate(total_students=Count('id'))
            .order_by('class_name_static')
        )

        class_wise_students = [
            {
                "class_name": item['class_name_static'],
                "total_students": item['total_students']
            }
            for item in class_wise_qs
        ]

        response_payload = {
            **summary_data,
            "class_wise_students": class_wise_students
        }

        serializer = SchoolDashboardStatsSerializer(data=response_payload)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
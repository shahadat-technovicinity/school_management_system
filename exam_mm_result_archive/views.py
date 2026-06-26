from rest_framework import generics, status
from apps.students.models import Student
from rest_framework.response import Response
from .models import *
from .serializers import *
from rest_framework.filters import SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class StudentFilterView(generics.ListAPIView):
    serializer_class = StudentInfoFilterSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('class_name', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True),
            openapi.Parameter('section', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=True),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Student.objects.none()

        class_name = self.request.query_params.get('class_name')
        section = self.request.query_params.get('section')

        if not class_name or not section:
            return Student.objects.none()

        return Student.objects.filter(
            class_name_static=class_name,
            section_static=section
        ).order_by('roll_number')





class MarksListCreateAPIView(generics.ListCreateAPIView):
    queryset = ExamMark.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return MarkSubmissionSerializer
        return MarksSerializer

    def create(self, request, *args, **kwargs):
        data = request.data

        # Bulk (list) নাকি Single (dict)?
        is_bulk = isinstance(data, list)
        marks_list = data if is_bulk else [data]

        saved = []
        errors = []

        for item in marks_list:
            serializer = MarkSubmissionSerializer(data=item)
            if serializer.is_valid():
                result = serializer.save()
                saved.append(result)
            else:
                errors.append(serializer.errors)

        if errors:
            return Response({"saved": saved, "errors": errors}, status=status.HTTP_207_MULTI_STATUS)

        return Response({"saved": saved, "message": f"{len(saved)} টি mark save হয়েছে"}, status=status.HTTP_201_CREATED)
    



##student mark and total view
class FinalResultView(generics.ListAPIView):
    serializer_class = FinalResultSerializer # FinalResultSerializer ব্যবহার হবে

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Student.objects.none()
            
        # Student মডেল ধরে ছাত্রদের তালিকা তৈরি করা হবে
        queryset = Student.objects.all() 
        
        class_name = self.request.query_params.get('class_name')
        section = self.request.query_params.get('section')
        exam_type = self.request.query_params.get('exam_type') # ⬅️ Exam Type ইনপুট নেওয়া হলো

        # class_name এবং section দিয়ে ছাত্রদের ফিল্টার করা
        if class_name:
            queryset = queryset.filter(class_name=class_name)
        if section:
            queryset = queryset.filter(section=section)
        
        # Serializer-কে ব্যবহারের জন্য exam_type কে instance ভেরিয়েবল হিসেবে সেভ করা হলো
        self.exam_type = exam_type
        
        return queryset

    def get_serializer_context(self):
        # context এর মাধ্যমে exam_type ডেটা FinalResultSerializer এ পাস করা হলো
        context = super().get_serializer_context()
        context['exam_type'] = self.exam_type
        return context
    

class MarkRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExamMark.objects.all()
    serializer_class = MarksSerializer




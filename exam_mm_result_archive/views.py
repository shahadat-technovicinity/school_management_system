from rest_framework import generics, status
from student_profile.models import StudentPersonalInfo
from rest_framework.response import Response
from .models import *
from .serializers import *


class StudentFilterView(generics.ListAPIView):
    serializer_class = StudentInfoFilterSerializer

    def get_queryset(self):
        queryset = StudentPersonalInfo.objects.all()
        class_name = self.request.query_params.get('class_name')
        section = self.request.query_params.get('section')

        if class_name:
            queryset = queryset.filter(class_name=class_name)
        if section:
            queryset = queryset.filter(section=section)

        return queryset.order_by('roll_number')





class MarksListCreateAPIView(generics.ListCreateAPIView):
    # GET রিকোয়েস্টে সমস্ত সেভ হওয়া মার্কস দেখতে পাবে
    queryset = ExamMark.objects.all() 

    def get_serializer_class(self):
        # যদি POST রিকোয়েস্ট হয় (সেভ করার জন্য), MarkSubmissionSerializer ব্যবহার হবে
        if self.request.method == 'POST':
            return MarkSubmissionSerializer
        # যদি GET রিকোয়েস্ট হয় (লিস্ট দেখার জন্য), MarksSerializer ব্যবহার হবে
        return MarksSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # serializer.save() কল করলে MarkSubmissionSerializer-এর create() মেথডটি রান হবে
        response_data = serializer.save() 
        
        # ডেটা সফলভাবে সেভ হলে 201 Created স্ট্যাটাস পাঠানো হবে
        return Response(response_data, status=status.HTTP_201_CREATED)
    



##student mark and total view
class FinalResultView(generics.ListAPIView):
    serializer_class = FinalResultSerializer # FinalResultSerializer ব্যবহার হবে

    def get_queryset(self):
        # StudentPersonalInfo মডেল ধরে ছাত্রদের তালিকা তৈরি করা হবে
        queryset = StudentPersonalInfo.objects.all() 
        
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
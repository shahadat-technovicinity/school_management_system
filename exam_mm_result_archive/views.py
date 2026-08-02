from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.students.models import Student
from .models import ExamMark
from .serializers import (
    StudentInfoFilterSerializer,
    MarkSubmissionSerializer,
    MarksSerializer,
    MarkStatusUpdateSerializer,
    FinalResultSerializer
)


# --- 1. Student Filter View ---
class StudentFilterView(generics.ListAPIView):
    serializer_class = StudentInfoFilterSerializer
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('class_name', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False, description="Class name e.g. Six"),
            openapi.Parameter('section', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False, description="Section e.g. A"),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Student.objects.none()

        queryset = Student.objects.all().order_by('roll_number')

        # Query param থেকে ভ্যালু নেওয়া (অতিরিক্ত স্পেস থাকলে strip করে দেবে)
        class_name = self.request.query_params.get('class_name', '').strip()
        section = self.request.query_params.get('section', '').strip()

        # class_name দিলে ফিল্টার করবে
        if class_name:
            queryset = queryset.filter(class_name_static__icontains=class_name)

        # section দিলে ফিল্টার করবে
        if section:
            queryset = queryset.filter(section_static__icontains=section)

        return queryset


# --- 2. Main Marks List (STRICTLY PENDING) & Create (GET / POST) ---
# GET: শুধু 'pending' মার্কস দেখাবে। Approved/Rejected হয়ে গেলে এখান থেকে হাওয়া হয়ে যাবে।
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


# --- 3. Single Mark Retrieve, Update, Delete ---
class MarkRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExamMark.objects.all()
    serializer_class = MarksSerializer
    permission_classes = [AllowAny]


# --- 4. Admin: Approved Marks List Only ---
class AdminApprovedMarksListAPIView(generics.ListAPIView):
    serializer_class = MarksSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ExamMark.objects.filter(status='approved').order_by('-updated_at')


# --- 5. Admin: Rejected Marks List Only ---
class AdminRejectedMarksListAPIView(generics.ListAPIView):
    serializer_class = MarksSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ExamMark.objects.filter(status='rejected').order_by('-updated_at')


# --- 6. Admin: Status Change Only (PATCH ONLY) ---
class AdminMarkStatusUpdateAPIView(generics.UpdateAPIView):
    queryset = ExamMark.objects.all()
    serializer_class = MarkStatusUpdateSerializer
    permission_classes = [AllowAny]
    http_method_names = ['patch']

    def perform_update(self, serializer):
        new_status = self.request.data.get('status')
        valid_status = [choice[0] for choice in ExamMark.STATUS_CHOICES]

        if not new_status or new_status not in valid_status:
            raise ValidationError({"detail": f"Invalid status. Must be one of {valid_status}."})

        serializer.save(status=new_status)


# --- 7. Final Result Sheet View ---
class FinalResultView(generics.ListAPIView):
    serializer_class = FinalResultSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Student.objects.none()
            
        queryset = Student.objects.all() 
        class_name = self.request.query_params.get('class_name')
        section = self.request.query_params.get('section')
        
        if class_name:
            queryset = queryset.filter(class_name=class_name)
        if section:
            queryset = queryset.filter(section=section)
        
        self.exam_type = self.request.query_params.get('exam_type')
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['exam_type'] = getattr(self, 'exam_type', None)
        return context
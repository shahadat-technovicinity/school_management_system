from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import IntegerField
from django.db.models.functions import Cast
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


# --- Pagination Setup ---
class StandardLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 100
    max_limit = 500


# --- 1. Student Filter View ---
class StudentFilterView(generics.ListAPIView):
    serializer_class = StudentInfoFilterSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardLimitOffsetPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('class_name', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False, description="Class ID"),
            openapi.Parameter('section', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False, description="Section ID"),
            openapi.Parameter('limit', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False, description="Limit"),
            openapi.Parameter('offset', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False, description="Offset"),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Student.objects.none()

        queryset = Student.objects.annotate(
            roll_int=Cast('roll_number', output_field=IntegerField())
        ).order_by('roll_int')

        class_name = self.request.query_params.get('class_name')
        section = self.request.query_params.get('section')

        if class_name:
            queryset = queryset.filter(class_name_static_id=class_name)
        if section:
            queryset = queryset.filter(section_static_id=section)

        return queryset


# --- 2. Main Marks List (STRICTLY PENDING) & Create ---
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


# --- 4. Admin Approved Marks ---
class AdminApprovedMarksListAPIView(generics.ListAPIView):
    serializer_class = MarksSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ExamMark.objects.filter(status='approved').order_by('-updated_at')


# --- 5. Admin Rejected Marks ---
class AdminRejectedMarksListAPIView(generics.ListAPIView):
    serializer_class = MarksSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ExamMark.objects.filter(status='rejected').order_by('-updated_at')


# --- 6. Admin Status Change (PATCH ONLY) ---
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
    pagination_class = StandardLimitOffsetPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('class_name', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False, description="Class ID"),
            openapi.Parameter('section', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False, description="Section ID"),
            openapi.Parameter('exam_type', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False, description="Exam Type ID"),
            openapi.Parameter('limit', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False, description="Limit"),
            openapi.Parameter('offset', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False, description="Offset"),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Student.objects.none()

        queryset = Student.objects.annotate(
            roll_int=Cast('roll_number', output_field=IntegerField())
        ).order_by('roll_int')
        
        class_name = self.request.query_params.get('class_name')
        section = self.request.query_params.get('section')
        
        if class_name:
            queryset = queryset.filter(class_name_static_id=class_name)
        if section:
            queryset = queryset.filter(section_static_id=section)
        
        self.exam_type = self.request.query_params.get('exam_type')
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['exam_type'] = getattr(self, 'exam_type', None)
        return context
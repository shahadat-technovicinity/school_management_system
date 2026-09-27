from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import LimitOffsetPagination
from django.db.models import IntegerField
from django.db.models.functions import Cast

from apps.students.models import Student
from .models import ExamMark, SubjectPassMarkConfig, GradeScale
from .serializers import (
    StudentInfoFilterSerializer,
    MarkSubmissionSerializer,
    MarksSerializer,
    MarkStatusUpdateSerializer,
    FinalResultSerializer,
    SubjectPassMarkConfigSerializer,
    GradeScaleSerializer
)


class StandardLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 100
    max_limit = 500


class SubjectPassMarkConfigListCreateAPIView(generics.ListCreateAPIView):
    queryset = SubjectPassMarkConfig.objects.all()
    serializer_class = SubjectPassMarkConfigSerializer
    permission_classes = [AllowAny]


class SubjectPassMarkConfigDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SubjectPassMarkConfig.objects.all()
    serializer_class = SubjectPassMarkConfigSerializer
    permission_classes = [AllowAny]


class GradeScaleListCreateAPIView(generics.ListCreateAPIView):
    queryset = GradeScale.objects.all()
    serializer_class = GradeScaleSerializer
    permission_classes = [AllowAny]


class GradeScaleDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GradeScale.objects.all()
    serializer_class = GradeScaleSerializer
    permission_classes = [AllowAny]


class StudentFilterView(generics.ListAPIView):
    serializer_class = StudentInfoFilterSerializer
    permission_classes = [AllowAny]
    pagination_class = StandardLimitOffsetPagination

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


class MarkRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExamMark.objects.all()
    serializer_class = MarksSerializer
    permission_classes = [AllowAny]


class AdminApprovedMarksListAPIView(generics.ListAPIView):
    serializer_class = MarksSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ExamMark.objects.filter(status='approved').order_by('-updated_at')


class AdminRejectedMarksListAPIView(generics.ListAPIView):
    serializer_class = MarksSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ExamMark.objects.filter(status='rejected').order_by('-updated_at')


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


class FinalResultSerializer(serializers.ModelSerializer):
    # Auto-generated primary key 'id'-কেই student_id হিসেবে দেখানোর নির্দেশ দেওয়া হলো
    student_id = serializers.IntegerField(source='id', read_only=True)
    
    total_marks = serializers.SerializerMethodField()
    gpa = serializers.SerializerMethodField()
    result_status = serializers.SerializerMethodField()
    merit_position = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = ['id', 'student_id', 'full_name', 'roll_number', 'total_marks', 'gpa', 'result_status', 'merit_position']

    def _is_swagger(self):
        request = self.context.get('request')
        if not request:
            return True
        return getattr(request.parser_context.get('view', None), 'swagger_fake_view', False)

    def get_total_marks(self, obj):
        if self._is_swagger():
            return 0.0
        exam_type = self.context.get('exam_type')
        marks = ExamMark.objects.filter(student=obj, status='approved')
        if exam_type:
            marks = marks.filter(exam_type_id=exam_type)
        return sum(m.total for m in marks)

    def get_gpa(self, obj):
        if self._is_swagger():
            return 0.0
        exam_type = self.context.get('exam_type')
        marks = ExamMark.objects.filter(student=obj, status='approved')
        if exam_type:
            marks = marks.filter(exam_type_id=exam_type)

        if not marks.exists() or any(not m.is_passed for m in marks):
            return 0.0

        total_gp = sum(m.grade_point for m in marks)
        return round(total_gp / marks.count(), 2)

    def get_result_status(self, obj):
        if self._is_swagger():
            return "PASSED"
        return "PASSED" if self.get_gpa(obj) > 0 else "FAILED"

    def get_merit_position(self, obj):
        if self._is_swagger():
            return 1
        merit_map = self.context.get('merit_map', {})
        return merit_map.get(obj.id, None)
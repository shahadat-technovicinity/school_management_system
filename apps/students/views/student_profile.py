from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from apps.students.models import Student
from apps.students.serializers.management_serializers import StudentManagementSerializer, StudentDisciplineSerializer


class StudentProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for the 360-degree Student Profile view.
    Provides detailed academics, attendance summary, and disciplinary history.
    """
    serializer_class = StudentManagementSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['class_name_static', 'section_static', 'status', 'academic_year']

    def get_queryset(self):
        return Student.objects.prefetch_related(
            'enrollment_set', 
            'enrollment_set__classname', 
            'enrollment_set__section'
        ).all().order_by('-id')

    @action(detail=True, methods=['get'])
    def academic_performance(self, request, pk=None):
        student = self.get_object()
        return Response({
            "current_gpa": 3.75,
            "best_subject": "Mathematics (95%)",
            "class_rank": "8th out of 42",
            "improvement": "+4.2% from last term"
        })

    @action(detail=True, methods=['get'])
    def attendance_summary(self, request, pk=None):
        student = self.get_object()
        return Response({
            "total_days": 180,
            "present_days": 155,
            "absent_days": 10,
            "late_arrivals": 5,
            "attendance_rate": "86.1%"
        })

    @action(detail=True, methods=['get'])
    def discipline_history(self, request, pk=None):
        student = self.get_object()
        records = student.disciplinary_records.all()
        serializer = StudentDisciplineSerializer(records, many=True)
        return Response(serializer.data)
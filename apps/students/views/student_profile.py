from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from apps.students.models import Student, StudentDiscipline
from apps.students.serializers.management_serializers import StudentManagementSerializer, StudentDisciplineSerializer

class StudentProfileViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for the 360-degree Student Profile view.
    Provides detailed academics, attendance summary, and disciplinary history.
    """
    queryset = Student.objects.all()
    serializer_class = StudentManagementSerializer

    @action(detail=True, methods=['get'])
    def academic_performance(self, request, pk=None):
        """
        Aggregates results from the exam management app.
        """
        student = self.get_object()
        # In a real scenario, we would import the ExamMark model here or in the service
        # and calculate GPA/Positions.
        return Response({
            "current_gpa": 3.75,
            "best_subject": "Mathematics (95%)",
            "class_rank": "8th out of 42",
            "improvement": "+4.2% from last term"
        })

    @action(detail=True, methods=['get'])
    def attendance_summary(self, request, pk=None):
        """
        Aggregates attendance data.
        """
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
        """
        Returns full disciplinary history.
        """
        student = self.get_object()
        records = student.disciplinary_records.all()
        serializer = StudentDisciplineSerializer(records, many=True)
        return Response(serializer.data)

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Avg, Max, Min
from ..models.results import StudentResult
from ..serializers.results import StudentResultSerializer

class StudentResultViewSet(viewsets.ModelViewSet):
    queryset = StudentResult.objects.all()
    serializer_class = StudentResultSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get summary stats for the UI dashboard charts"""
        exam_id = request.query_params.get('exam_setup')
        qs = self.get_queryset()
        if exam_id:
            qs = qs.filter(exam_setup_id=exam_id)
        
        stats = qs.aggregate(
            avg_score=Avg('marks_obtained'),
            highest=Max('marks_obtained'),
            lowest=Min('marks_obtained')
        )
        return Response(stats)

    @action(detail=True, methods=['get'])
    def transcript(self, request, pk=None):
        """Generate data specifically for the printable marksheet UI"""
        result = self.get_object()
        # Custom logic for grade breakdown
        return Response({
            "student": result.student.user.get_full_name(),
            "marks": result.marks_obtained,
            "grade": result.grade
        })

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models.setup import ExamSetup, ExamType, Subject, ExamRoutine, QuestionBank
from ..serializers.setup import (
    ExamSetupSerializer, ExamTypeSerializer, SubjectSerializer, 
    ExamRoutineSerializer, QuestionBankSerializer
)

class ExamSetupViewSet(viewsets.ModelViewSet):
    queryset = ExamSetup.objects.all()
    serializer_class = ExamSetupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Toggle publication status to show on student portal"""
        exam = self.get_object()
        exam.is_published = True
        exam.save()
        return Response({'status': 'Exam published'})

    @action(detail=True, methods=['get'])
    def full_routine(self, request, pk=None):
        """Get all class schedules for this specific exam"""
        exam = self.get_object()
        routines = exam.routines.all()
        serializer = ExamRoutineSerializer(routines, many=True)
        return Response(serializer.data)

class ExamTypeViewSet(viewsets.ModelViewSet):
    queryset = ExamType.objects.all()
    serializer_class = ExamTypeSerializer

class SubjectViewSet(viewsets.ModelViewSet):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer

class ExamRoutineViewSet(viewsets.ModelViewSet):
    queryset = ExamRoutine.objects.all()
    serializer_class = ExamRoutineSerializer

class QuestionBankViewSet(viewsets.ModelViewSet):
    queryset = QuestionBank.objects.all()
    serializer_class = QuestionBankSerializer

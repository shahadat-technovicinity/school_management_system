from rest_framework import viewsets, permissions
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

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

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

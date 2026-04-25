from rest_framework import viewsets, permissions
from ..models.logistics import ExamAdmitCard, ExamSeatPlan, TeacherDuty
from ..serializers.logistics import (
    ExamAdmitCardSerializer, ExamSeatPlanSerializer, TeacherDutySerializer
)

class ExamAdmitCardViewSet(viewsets.ModelViewSet):
    queryset = ExamAdmitCard.objects.all()
    serializer_class = ExamAdmitCardSerializer

class ExamSeatPlanViewSet(viewsets.ModelViewSet):
    queryset = ExamSeatPlan.objects.all()
    serializer_class = ExamSeatPlanSerializer

class TeacherDutyViewSet(viewsets.ModelViewSet):
    queryset = TeacherDuty.objects.all()
    serializer_class = TeacherDutySerializer

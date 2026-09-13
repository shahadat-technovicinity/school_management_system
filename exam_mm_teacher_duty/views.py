from rest_framework import generics
from .models import ExamDuty
from .serializers import ExamDutySerializer, ExamDutyStatusUpdateSerializer


class ExamDutyListCreateView(generics.ListCreateAPIView):
    """
    List all exam duties or assign a new teacher duty (Default status: Pending).
    """
    queryset = ExamDuty.objects.select_related('teacher').all()
    serializer_class = ExamDutySerializer


class ExamDutyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a specific teacher duty.
    """
    queryset = ExamDuty.objects.all()
    serializer_class = ExamDutySerializer


class ExamDutyStatusUpdateView(generics.UpdateAPIView):
    """
    Update only the status of an exam duty (Pending / Confirmed / Conflict).
    """
    queryset = ExamDuty.objects.all()
    serializer_class = ExamDutyStatusUpdateSerializer
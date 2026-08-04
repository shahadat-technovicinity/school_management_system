from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone

from .models import ExamDuty
from .serializers import ExamDutySerializer, ExamDutyStatusUpdateSerializer


class ExamDutyListCreateView(generics.ListCreateAPIView):
    """মূল duty লিস্ট - এখানে আজ ও ভবিষ্যতের সব duty দেখাবে (archive বাদে)"""
    serializer_class = ExamDutySerializer

    def get_queryset(self):
        return ExamDuty.objects.filter(exam_date__gte=timezone.now().date())

    def perform_create(self, serializer):
        duty = serializer.save()
        self.check_conflict(duty)

    def check_conflict(self, duty):
        clashes = ExamDuty.objects.filter(
            teacher=duty.teacher,
            exam_date=duty.exam_date,
            time_slot=duty.time_slot
        ).exclude(id=duty.id)

        if clashes.exists():
            duty.status = 'Conflict'
            duty.save()
            clashes.update(status='Conflict')


class ExamDutyDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExamDuty.objects.all()
    serializer_class = ExamDutySerializer


class ExamDutyStatusUpdateView(generics.UpdateAPIView):
    """PATCH দিয়ে শুধু status বদলানোর জন্য (Pending -> Confirmed)"""
    queryset = ExamDuty.objects.all()
    serializer_class = ExamDutyStatusUpdateSerializer


class ArchivedExamDutyListView(generics.ListAPIView):
    """Archive - exam_date গতকাল বা তার আগে চলে গেছে"""
    serializer_class = ExamDutySerializer

    def get_queryset(self):
        return ExamDuty.objects.filter(exam_date__lt=timezone.now().date())


class DutyStatsView(APIView):
    """Dashboard এর নিচের stats: Total, Pending, Conflicts"""

    def get(self, request):
        total = ExamDuty.objects.count()
        pending = ExamDuty.objects.filter(status='Pending').count()
        conflicts = ExamDuty.objects.filter(status='Conflict').count()
        confirmed = ExamDuty.objects.filter(status='Confirmed').count()

        return Response({
            "total_assignments": total,
            "pending_confirmations": pending,
            "assignment_conflicts": conflicts,
            "confirmed": confirmed,
        })
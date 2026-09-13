from rest_framework import generics
from .models import ExamRoutine
from .serializers import ExamRoutineSerializer


class ExamRoutineListCreateView(generics.ListCreateAPIView):
    queryset = ExamRoutine.objects.select_related(
        'exam_name', 
        'academic_class',
        'subject',
        'exam_setup'
    ).prefetch_related(
        'exam_setup__sections'
    ).all()
    serializer_class = ExamRoutineSerializer


class ExamRoutineDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExamRoutine.objects.all()
    serializer_class = ExamRoutineSerializer
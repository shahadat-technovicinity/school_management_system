from rest_framework import generics
from .models import ExamName, ExamSetup
from .serializers import ExamNameSerializer, ExamSetupSerializer

# Exam Name APIs
class ExamNameListCreateView(generics.ListCreateAPIView):
    queryset = ExamName.objects.all().order_by('-id')
    serializer_class = ExamNameSerializer


class ExamNameDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExamName.objects.all()
    serializer_class = ExamNameSerializer


# Exam Setup APIs
class ExamSetupListCreateView(generics.ListCreateAPIView):
    queryset = ExamSetup.objects.select_related(
        'exam_name', 
        'academic_class'
    ).prefetch_related(
        'sections'
    ).all().order_by('-id')
    
    serializer_class = ExamSetupSerializer


class ExamSetupDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExamSetup.objects.all()
    serializer_class = ExamSetupSerializer
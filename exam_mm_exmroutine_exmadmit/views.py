from django.shortcuts import render

# Create your views here.
from rest_framework import generics
from .models import *
from .serializers import *

class ExamRoutineListCreateView(generics.ListCreateAPIView):
    queryset = ExamRoutine.objects.all()
    serializer_class = ExamRoutineAdmit


class ExamRoutineDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExamRoutine.objects.all()
    serializer_class = ExamRoutineAdmit


####admit header

class ExamAdmitListCreateView(generics.ListCreateAPIView):
    queryset = ExamAdmit.objects.all()
    serializer_class = ExamAdmitSerializer


class ExamAdmitDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExamAdmit.objects.all()
    serializer_class = ExamAdmitSerializer
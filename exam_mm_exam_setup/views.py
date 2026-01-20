from django.shortcuts import render
from rest_framework import viewsets
from .models import *
from .serializers import *

class ExamSetupViewSet(viewsets.ModelViewSet):
    queryset = exm_mm_exam_setup.objects.all()
    serializer_class = ExamSerializer
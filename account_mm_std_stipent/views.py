from django.shortcuts import render
from rest_framework import generics
from .models import *
from .serializers import *
# Create your views here.
class stipent_student_listcreate(generics.ListCreateAPIView):
    queryset = stipend_student.objects.all()
    serializer_class = stipend_stu_serializer


class stipent_student_retrievedestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = stipend_student.objects.all()
    serializer_class = stipend_stu_serializer


class stipent_free_hf_listcreate(generics.ListCreateAPIView):
    queryset = stipend_free_hf.objects.all()
    serializer_class = stipend_free_hf_serializer


class stipent_free_hf_retrievedestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = stipend_free_hf.objects.all()
    serializer_class = stipend_free_hf_serializer
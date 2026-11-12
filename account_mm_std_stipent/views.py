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
    serializer_class = stipend_free_hf_serializer

    def get_queryset(self):
        qs = stipend_free_hf.objects.select_related('student').prefetch_related('fee_heads').order_by('-id')
        p = self.request.query_params
        if p.get('student'):
            qs = qs.filter(student_id=p['student'])
        if p.get('status'):
            qs = qs.filter(status=p['status'])
        return qs


class stipent_free_hf_retrievedestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = stipend_free_hf.objects.select_related('student').prefetch_related('fee_heads')
    serializer_class = stipend_free_hf_serializer
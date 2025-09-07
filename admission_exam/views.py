from django.shortcuts import render
from rest_framework.generics import ListAPIView, ListCreateAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView, RetrieveUpdateDestroyAPIView
from rest_framework import viewsets
from .models import *
from .serializers import *
# from .serializers import StudentAdmissionMainSerializer


##############  create method  #########################
class std_admission_exam(ListCreateAPIView):
    queryset = student_admission_exam.objects.all()
    serializer_class = Student_admission_exam_serializer

    def perform_create(self, serializer):
        """
        user save
        """
        serializer.save()


# ############# get method ##############
# class student_exam_get(ListAPIView):
#     queryset = student_admission_exam.objects.all()
#     serializer_class = Student_admission_exam_serializer


# #admission exam delete
# class addmissionexamdelete(DestroyAPIView):
#     queryset = student_admission_exam.objects.all()  #all user call
#     serializer_class = Student_admission_exam_serializer  #serializer class call serializer
#     lookup_field = 'id'  


class StdExmRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
    queryset = student_admission_exam.objects.all()
    serializer_class = Student_admission_exam_serializer  

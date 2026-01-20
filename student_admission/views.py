from django.shortcuts import render
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework import viewsets
from .models import *
from .serializers import *
from rest_framework.parsers import MultiPartParser, FormParser
# from .serializers import StudentAdmissionMainSerializer


##############  create method  #########################
class stident_info_createapiview(CreateAPIView):
    queryset = StudentAdmission.objects.all()
    serializer_class = StudentInfoSerializer
    parser_classes = (MultiPartParser, FormParser,)

    def perform_create(self, serializer):
        """
        user save
        """
        serializer.save()


############# get method ##############
class student_info_get(ListAPIView):
    queryset = StudentAdmission.objects.all()
    serializer_class = StudentInfoSerializer

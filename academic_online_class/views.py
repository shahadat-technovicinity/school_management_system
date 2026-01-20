from django.shortcuts import render
from rest_framework.generics import ListAPIView, ListCreateAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView, RetrieveUpdateDestroyAPIView
from .models import *
from .serializers import *
# from .serializers import StudentAdmissionMainSerializer


##############  create method  #########################
class Onlineclass(ListCreateAPIView):
    queryset = academiconlineclass.objects.all()
    serializer_class = AOCSerializer

    def perform_create(self, serializer):
        """
        user save
        """
        serializer.save()



# #academic online class delete
class onlineclassdelete(DestroyAPIView):
    queryset = academiconlineclass.objects.all()  #all user call
    serializer_class = AOCSerializer  #serializer class call serializer
    lookup_field = 'id'  


# class StdExmRetrieveUpdateDestroyAPIView(RetrieveUpdateDestroyAPIView):
#     queryset = student_admission_exam.objects.all()
#     serializer_class = Student_admission_exam_serializer  

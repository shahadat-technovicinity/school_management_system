# views.py file
from rest_framework.generics import ListAPIView, ListCreateAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView, RetrieveUpdateDestroyAPIView
from .models import *
from .serializers import *
class StudentProfileCreate(ListCreateAPIView):
    queryset = StudentPersonalInfo.objects.all()
    serializer_class = StudentFullSerializer


class StudentProfileUpdateDelete(RetrieveUpdateDestroyAPIView):
    queryset = StudentPersonalInfo.objects.all()
    serializer_class = StudentFullSerializer  
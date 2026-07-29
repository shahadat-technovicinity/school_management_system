# class_routine/views.py
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import ClassRoutine
from .serializers import *


User = get_user_model()

# teacher fetch view
class TeacherListView(ListAPIView):
    queryset = User.objects.filter(role__name='Teacher').order_by('-id')
    serializer_class = TeacherListSerializer


## GET, POST
class ClassRoutineView(ListCreateAPIView):
    # order_by('-id') যোগ করা হয়েছে যাতে নতুন রুটিনগুলো সবার আগে আসে এবং UnorderedObjectListWarning দূর হয়
    queryset = ClassRoutine.objects.all().order_by('-id')
    serializer_class = ClassRoutineSerializer


## GET, PUT, PATCH, DELETE
class ClassRoutineupdateDelete(RetrieveUpdateDestroyAPIView):
    queryset = ClassRoutine.objects.all().order_by('-id')
    serializer_class = ClassRoutineSerializer
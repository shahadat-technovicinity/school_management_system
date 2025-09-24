# class_routine/views.py
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import ClassRoutine
from .serializers import *


# academic_management/views.py
### authentication teacher fetch
User = get_user_model()
class TeacherListView(ListAPIView):
    queryset = User.objects.filter(role='Teacher')
    serializer_class = TeacherListSerializer

    
# class ClassRoutineCreate(CreateAPIView):
#     queryset = ClassRoutine.objects.all()
#     serializer_class = ClassRoutineSerializer

## get, post
User = get_user_model()

class ClassRoutineView(ListCreateAPIView):
    queryset = ClassRoutine.objects.all()
    serializer_class = ClassRoutineSerializer


#get, put, patch, delete
class ClassRoutineupdateDelete(RetrieveUpdateDestroyAPIView):
    queryset = ClassRoutine.objects.all()
    serializer_class = ClassRoutineSerializer  

from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated # Eita byabohar kora uchit
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import *
from .serializers import *



User = get_user_model()

class TeacherStaffListView(generics.ListAPIView):
    # queryset attribute-ti muche deya holo
    serializer_class = TeacherStaffListSerializer

    def get_queryset(self):
        # Ekhon filtering logic-ti method-er modhye dynamically kaaj korche
        return User.objects.filter(
            Q(role='Teacher') | Q(role='Staff'), # Teacher OR Staff
            # is_active=True # AND active
        )



class TeacherStaffWorkView(generics.ListCreateAPIView):
    queryset = WorkAssignment.objects.all()
    serializer_class = WorkAssignmentSerializer


#get, put, patch, delete
class TeacherStaffWorkUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = WorkAssignment.objects.all()
    serializer_class = WorkAssignmentSerializer  


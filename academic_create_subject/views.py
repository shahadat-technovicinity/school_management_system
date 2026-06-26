from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Subject_Name
from .serializers import Subject_Name_Serializer


class SubjectListCreateView(generics.ListCreateAPIView):
    queryset = Subject_Name.objects.all().order_by('name')
    serializer_class = Subject_Name_Serializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


class SubjectRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Subject_Name.objects.all()
    serializer_class = Subject_Name_Serializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
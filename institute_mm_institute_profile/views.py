from django.shortcuts import render
from rest_framework import generics
from .serializers import *
from .models import *

# institute info.
class InstitutionListCreateView(generics.ListCreateAPIView):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer


class InstitutionInfoView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
    


#########Institute details page
class InstitutiondetailsListCreateView(generics.ListCreateAPIView):
    queryset = InstitutionDetails.objects.all()
    serializer_class = InstitutionDetailsSerializer


class InstitutionDetailpageView(generics.RetrieveUpdateDestroyAPIView):
    queryset = InstitutionDetails.objects.all()
    serializer_class = InstitutionDetailsSerializer
from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import generics

# Create your views here.
class Facility_asset(generics.ListCreateAPIView):
    queryset = FacilityFurnitureItem.objects.all()
    serializer_class = FacilityFurnitureSerializer


class Facility_assetupdatedelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = FacilityFurnitureItem.objects.all()
    serializer_class = FacilityFurnitureSerializer
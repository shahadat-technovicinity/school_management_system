from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import generics

# Create your views here.
class income_collect(generics.ListCreateAPIView):
    queryset = account_Income.objects.all()
    serializer_class = account_income_serializer

class income_collect_retrievedestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = account_Income.objects.all()
    serializer_class = account_income_serializer
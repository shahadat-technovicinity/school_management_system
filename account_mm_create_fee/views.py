from django.shortcuts import render
from .models import *
from .serializers import *
from rest_framework import generics

# Create your views here.
class FeeCreate(generics.ListCreateAPIView):
    queryset = CreateFee.objects.all()
    serializer_class = CreateFeeSerializer

# class income_collect_retrievedestroy(generics.RetrieveUpdateDestroyAPIView):
#     queryset = account_Income.objects.all()
#     serializer_class = account_income_serializer


# class CreateFeeListCreateAPIView(generics.ListCreateAPIView):
#     queryset = CreateFee.objects.all() 
#     serializer_class = CreateFeeSerializer
    
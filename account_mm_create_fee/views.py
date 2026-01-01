from rest_framework import generics, status
from rest_framework.response import Response
from .models import *
from .serializers import *

class FeeListCreateView(generics.ListCreateAPIView):
    queryset = CreateFee.objects.all()
    serializer_class = CreateFeeSerializer


class FeeCreateUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = CreateFee.objects.all()
    serializer_class = CreateFeeSerializer



class FormFilupListCreateView(generics.ListCreateAPIView):
    queryset = FormFilupAmount.objects.all()
    serializer_class = FormFilupAmountSerializer


class FormFilupUpdateDelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = FormFilupAmount.objects.all()
    serializer_class = FormFilupAmountSerializer


        
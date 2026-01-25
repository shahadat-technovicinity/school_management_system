from django.shortcuts import render
from rest_framework import generics
from .models import *
from .serializers import *
from rest_framework.pagination import PageNumberPagination

# Create your views here.
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10

class Book_list_create_get_api(generics.ListCreateAPIView):
    queryset = Book_model.objects.all()
    serializer_class = Book_model_serializers
    pagination_class = StandardResultsSetPagination


class Book_model_get_update_delete_api(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book_model.objects.all()
    serializer_class = Book_model_serializers

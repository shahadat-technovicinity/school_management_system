from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import *
from .serializers import *

# Student List (Table) ebong Student Add (Form) er jonno
class StudentTopListCreateView(generics.ListCreateAPIView):
    queryset = StudentTop.objects.all().order_by('roll')
    serializer_class = StudentTopSerializer
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['class_name', 'section', 'subject', 'achievement']
    search_fields = ['student_name', 'roll', 'mobile_no']

# Student Update (Edit), Delete, ebong View (Details) er jonno
class StudentTopDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentTop.objects.all()
    serializer_class = StudentTopSerializer
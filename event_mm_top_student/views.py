from rest_framework import generics, filters
from .models import *
from .serializers import *
from rest_framework.parsers import MultiPartParser, FormParser


# List and Create (GET / POST)
class Top_StudentListCreateView(generics.ListCreateAPIView):
    queryset = Top_Student.objects.all().order_by('-id')
    serializer_class = Top_StudentSerializer
    parser_classes = (MultiPartParser, FormParser)
    
    # Adding Search & Filtering logic for the UI filters
    filter_backends = [filters.SearchFilter]
    search_fields = ['student_name', 'roll', 'student_class', 'section']

# Retrieve, Update, and Delete (GET / PUT / PATCH / DELETE)
class Top_StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Top_Student.objects.all()
    serializer_class = Top_StudentSerializer
    lookup_field = 'pk'
    parser_classes = (MultiPartParser, FormParser)
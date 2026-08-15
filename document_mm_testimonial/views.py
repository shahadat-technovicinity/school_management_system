from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from .models import StudentApplication
from .serializers import StudentApplicationSerializer, StudentApplicationStatusUpdateSerializer

class StudentApplicationListCreateView(generics.ListCreateAPIView):
    queryset = StudentApplication.objects.all().order_by('-created_at')
    serializer_class = StudentApplicationSerializer
    pagination_class = PageNumberPagination

class StudentApplicationDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentApplication.objects.all()
    serializer_class = StudentApplicationSerializer

class StudentApplicationStatusUpdateView(generics.UpdateAPIView):
    queryset = StudentApplication.objects.all()
    serializer_class = StudentApplicationStatusUpdateSerializer
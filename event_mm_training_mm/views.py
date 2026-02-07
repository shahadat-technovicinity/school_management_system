from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import TrainingRecord
from .serializers import TrainingRecordSerializer

# List dekhano ebong Notun Training add kora
class TrainingListCreateView(generics.ListCreateAPIView):
    queryset = TrainingRecord.objects.all().order_by('-date_to')
    serializer_class = TrainingRecordSerializer
    
    # Filtering ebong Search logic
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['authority', 'status'] # Figma-r "All Authorities" dropdown filter
    search_fields = ['teacher_id', 'training_name'] # Figma-r Search bar toggle

# Edit, Delete ba Specific record view
class TrainingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TrainingRecord.objects.all()
    serializer_class = TrainingRecordSerializer
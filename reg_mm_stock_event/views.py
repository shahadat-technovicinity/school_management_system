from rest_framework import generics, filters
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import StockInventory
from .serializers import StockInventorySerializer

class StockListCreateAPIView(generics.ListCreateAPIView):
    queryset = StockInventory.objects.all().order_by('-created_at')
    serializer_class = StockInventorySerializer
    parser_classes = [MultiPartParser, FormParser]
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'location_or_sub_category']
    search_fields = ['item_name', 'item_id', 'location_or_sub_category']

class StockDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StockInventory.objects.all()
    serializer_class = StockInventorySerializer
    parser_classes = [MultiPartParser, FormParser]
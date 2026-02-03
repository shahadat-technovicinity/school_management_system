from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import generics
from .models import *
from .serializers import *

class FixedPhotoPagination(PageNumberPagination):
    page_size = 10  



class PhotoListCreateView(generics.ListCreateAPIView):
    queryset = PhotoGallery.objects.all().order_by('-created_at')
    serializer_class = PhotoGallerySerializer
    pagination_class = FixedPhotoPagination 


class PhotoRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PhotoGallery.objects.all()
    serializer_class = PhotoGallerySerializer





### video gallery views 



class VideoListCreateView(generics.ListCreateAPIView):
    queryset = VideoGallery.objects.all().order_by('-id')
    serializer_class = VideoGallerySerializer
    pagination_class = FixedPhotoPagination

class VideoRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = VideoGallery.objects.all()
    serializer_class = VideoGallerySerializer

from rest_framework import generics
from .models import *
from .serializers import *

class PicnicListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PicnicSerializer
    def get_queryset(self):
        queryset = Picnic.objects.all().order_by('-date')
        status = self.request.query_params.get('status')
        if status:
            return queryset.filter(status__iexact=status)
        return queryset

class PicnicRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Picnic.objects.all()
    serializer_class = PicnicSerializer
    lookup_field = 'id'

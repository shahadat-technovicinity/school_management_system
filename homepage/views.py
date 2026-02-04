from rest_framework import generics
from .models import *
from .serializers import *

class Home_Page_SliderListCreateView(generics.ListCreateAPIView):
    queryset = Home_Page_Slider.objects.all()
    serializer_class = Home_Page_SliderSerializer

class Home_Page_SliderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Home_Page_Slider.objects.all()
    serializer_class = Home_Page_SliderSerializer
    lookup_field = 'pk' 



#### Message Views
class MessageListCreateView(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

# Detail, Update, Delete View
class MessageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
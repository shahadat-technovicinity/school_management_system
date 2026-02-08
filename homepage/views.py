from rest_framework import generics
from .models import *
from .serializers import *
from rest_framework.parsers import MultiPartParser, FormParser

class Home_Page_SliderListCreateView(generics.ListCreateAPIView):
    queryset = Home_Page_Slider.objects.all()
    serializer_class = Home_Page_SliderSerializer
    parser_classes = (MultiPartParser, FormParser)

class Home_Page_SliderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Home_Page_Slider.objects.all()
    serializer_class = Home_Page_SliderSerializer
    lookup_field = 'pk' 
    parser_classes = (MultiPartParser, FormParser)



#### Message Views
class MessageListCreateView(generics.ListCreateAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

# Detail, Update, Delete View
class MessageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer



## Admission Notice Views
class AdmissionNoticeListCreateView(generics.ListCreateAPIView):
    queryset = AdmissionNotice.objects.all()
    serializer_class = AdmissionNoticeSerializer


class AdmissionNoticeRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AdmissionNotice.objects.all()
    serializer_class = AdmissionNoticeSerializer
    lookup_field = 'pk'




# Contact Message Views
class ContactMessageListCreateView(generics.ListCreateAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer


class ContactMessageRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    lookup_field = 'pk'



# Letter Info Views
class LetterInfoListCreateView(generics.ListCreateAPIView):
    queryset = LetterInfo.objects.all()
    serializer_class = LatterSerializer
    parser_classes = (MultiPartParser, FormParser)


class LetterInfoRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LetterInfo.objects.all()
    serializer_class = LatterSerializer
    lookup_field = 'pk'
    parser_classes = (MultiPartParser, FormParser)
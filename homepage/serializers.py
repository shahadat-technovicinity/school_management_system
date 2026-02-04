from rest_framework import serializers
from .models import *

# Home Page Slider Serializer
class Home_Page_SliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Home_Page_Slider
        fields = '__all__'


# Message Serializer
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'



# Admission Notice Serializer
class AdmissionNoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdmissionNotice
        fields = '__all__'



# Contact Message Serializer
class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__'



# Latter serializer
class LatterSerializer(serializers.ModelSerializer):
    class Meta:
        model = LetterInfo
        fields = '__all__'
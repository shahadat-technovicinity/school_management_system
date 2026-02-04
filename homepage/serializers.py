from rest_framework import serializers
from .models import *

class Home_Page_SliderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Home_Page_Slider
        fields = '__all__'


# Message Serializer
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'
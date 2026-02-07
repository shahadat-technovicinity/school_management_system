from rest_framework import serializers
from .models import *

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event_mm_Achievement
        fields = '__all__'
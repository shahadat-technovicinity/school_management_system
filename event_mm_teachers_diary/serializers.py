from rest_framework import serializers
from .models import *

class TeacherDiarySerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherDiary
        fields = '__all__'
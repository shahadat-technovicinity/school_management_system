from rest_framework import serializers
from .models import *

class StudentTopSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentTop
        fields = '__all__'
# admissions/serializers.py

from rest_framework import serializers
from .models import *


class AOCSerializer(serializers.ModelSerializer):
    class Meta:
        model = academiconlineclass
        fields = '__all__'
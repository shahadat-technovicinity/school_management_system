# exam / serializers.py
from rest_framework import serializers
from .models import *

class ExamSerializer(serializers.ModelSerializer):
    class Meta:
        model = exm_mm_exam_setup
        fields = "__all__"
# admissions/serializers.py

from rest_framework import serializers
from .models import *

class Student_admission_exam_serializer(serializers.ModelSerializer):
    class Meta:
        model = student_admission_exam
        fields = '__all__'

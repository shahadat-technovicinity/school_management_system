# admissions/serializers.py

from rest_framework import serializers
from .models import *

class ExamRoutineAdmit(serializers.ModelSerializer):
    class Meta:
        model = ExamRoutine
        fields = '__all__'


class ExamAdmitSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamAdmit
        fields = '__all__'
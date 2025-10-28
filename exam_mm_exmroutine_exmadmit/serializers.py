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



##### admit card summary dashboard serializer

class AdmitSummarySerializer(serializers.Serializer):
    generated = serializers.IntegerField()
    pending = serializers.IntegerField()
    total = serializers.IntegerField()
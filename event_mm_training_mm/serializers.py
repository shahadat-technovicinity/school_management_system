from rest_framework import serializers
from .models import TrainingRecord

class TrainingRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingRecord
        fields = '__all__'
from rest_framework import serializers
from .models import CrimeReport


class CrimeReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = CrimeReport
        fields = '__all__'
        extra_kwargs = {
            'case_number': {'required': False},
            'plaintiff': {'required': False},
            'defendant': {'required': False},
            'subject': {'required': False},
            'date_filed': {'required': False},
        }
# institution/serializers.py
from rest_framework import serializers
from .models import *

class InstitutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institution
        fields = '__all__'


class InstitutionDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstitutionDetails
        fields = '__all__'
from rest_framework import serializers
from .models import *

class FacilityFurnitureSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacilityFurnitureItem
        fields = '__all__'

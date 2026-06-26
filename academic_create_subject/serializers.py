from rest_framework import serializers
from .models import Subject_Name

class Subject_Name_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Subject_Name
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model

User = get_user_model()
class TeacherStaffListSerializer(serializers.ModelSerializer):
    label = serializers.CharField(source="name", read_only=True)
    value = serializers.IntegerField(source="id", read_only=True)

    class Meta:
        model = User
        fields = ["value", "label"]



class WorkAssignmentSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    
    class Meta:
        model = WorkAssignment
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

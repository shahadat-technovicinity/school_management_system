from rest_framework import serializers
from ..models import WorkAssignment

class WorkAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkAssignment
        fields = '__all__'

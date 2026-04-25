from rest_framework import serializers
from ..models.results import StudentResult

class StudentResultSerializer(serializers.ModelSerializer):
    student_name = serializers.ReadOnlyField(source='student.user.get_full_name')
    
    class Meta:
        model = StudentResult
        fields = '__all__'

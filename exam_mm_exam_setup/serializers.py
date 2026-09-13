from rest_framework import serializers
from .models import ExamName, ExamSetup

class ExamNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamName
        fields = ['id', 'name', 'description', 'is_active', 'created_at']


class ExamSetupSerializer(serializers.ModelSerializer):
    exam_name_title = serializers.ReadOnlyField(source='exam_name.name')
    class_name_text = serializers.ReadOnlyField(source='academic_class.name')
    section_names = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field='name', source='sections'
    )

    class Meta:
        model = ExamSetup
        fields = [
            'id', 
            'exam_name', 
            'exam_name_title', 
            'academic_class', 
            'class_name_text',
            'sections', 
            'section_names', 
            'shift', 
            'created_at'
        ]
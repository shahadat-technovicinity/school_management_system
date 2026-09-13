from rest_framework import serializers
from .models import QuestionBank
from academic_mm_class_and_section.models import Section


class SectionMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', 'name']


class QuestionBankSerializer(serializers.ModelSerializer):
    academic_class_name = serializers.CharField(source='academic_class.name', read_only=True)
    subject_name = serializers.CharField(source='subject.subject_name', read_only=True)
    sections_details = SectionMiniSerializer(source='sections', many=True, read_only=True)

    class Meta:
        model = QuestionBank
        fields = [
            'id', 
            'title', 
            'academic_class', 
            'academic_class_name', 
            'subject', 
            'subject_name', 
            'sections', 
            'sections_details', 
            'file', 
            'status', 
            'uploaded_by', 
            'created_at', 
            'updated_at'
        ]
        read_only_fields = ['status', 'uploaded_by', 'created_at', 'updated_at']

    def to_internal_value(self, data):
        # Multipart form-data handling for sections input
        if hasattr(data, 'getlist'):
            sections = data.getlist('sections')
            if sections:
                flat_sections = []
                for s in sections:
                    if isinstance(s, str) and ',' in s:
                        flat_sections.extend([item.strip() for item in s.split(',')])
                    else:
                        flat_sections.append(s)
                
                mutable_data = data.copy()
                mutable_data.setlist('sections', flat_sections)
                data = mutable_data

        return super().to_internal_value(data)


class QuestionBankStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionBank
        fields = ['status']

    def validate_status(self, value):
        if value not in ['approved', 'rejected']:
            raise serializers.ValidationError("Status can only be updated to 'approved' or 'rejected'.")
        return value
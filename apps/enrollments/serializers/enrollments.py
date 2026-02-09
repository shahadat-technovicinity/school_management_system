from rest_framework import serializers

from apps.enrollments.models import Enrollment

class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = "__all__"
        read_only_fields = ('created_at', 'updated_at', 'created_by', 'updated_by')
        extra_kwargs = {
            'student': {'required': True},
            'class_section': {'required': True},
            'academic_year': {'required': True}
        }
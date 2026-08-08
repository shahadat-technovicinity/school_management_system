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


class BulkEnrollmentSerializer(serializers.Serializer):
    student_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
        help_text="List of Student IDs to enroll",
    )
    classname = serializers.CharField(max_length=256, help_text="Class name for enrollment")
    section = serializers.CharField(max_length=256, default="A", help_text="Section (default: A)")
    academic_year = serializers.CharField(max_length=256, required=False, help_text="Academic year (defaults to active year)")

from rest_framework import serializers
from apps.enrollments.models import Enrollment


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'classname', 'section', 'academic_year']
        read_only_fields = ('id',)
        extra_kwargs = {
            'student': {'required': True},
            'classname': {'required': True},
            'section': {'required': True},
            'academic_year': {'required': True}
        }


class StudentEnrollmentItemSerializer(serializers.Serializer):
    student_id = serializers.IntegerField(min_value=1)


class BulkEnrollmentSerializer(serializers.Serializer):
    students = StudentEnrollmentItemSerializer(many=True, allow_empty=False)
    classname = serializers.IntegerField(help_text="Class ID")
    section = serializers.IntegerField(help_text="Section ID")
    academic_year = serializers.IntegerField(required=False, help_text="Academic Year ID (optional)")
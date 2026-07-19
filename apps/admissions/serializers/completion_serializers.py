from rest_framework import serializers
from apps.admissions.models import StudentAdmission


class CompletedAdmissionSerializer(serializers.ModelSerializer):
    """Read-only serializer for listing selected (not-yet-enrolled) applicants."""
    skill_names = serializers.SerializerMethodField()

    class Meta:
        model = StudentAdmission
        fields = [
            'id',
            'application_number',
            'admin_form_number',
            'student_name_english',
            'student_name_bangla',
            'desired_class',
            'gender',
            'admission_status',
            'skill_names',
        ]
        read_only_fields = fields

    def get_skill_names(self, obj):
        return [link.skill.name for link in obj.skills.all()]
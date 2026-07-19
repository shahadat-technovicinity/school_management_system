from rest_framework import serializers
from apps.admissions.models import StudentAdmission


class FinalizeAdmissionSerializer(serializers.Serializer):
    """
    Documents the documents payload expected by the `finalize` action.
    Files are sent as multipart/form-data; keys are treated as document_type.
    """
    # Read-only mirror of the fields we expose back after finalizing.
    tc = serializers.FileField(required=False, help_text="Transfer Certificate")
    mother_nid = serializers.FileField(required=False, help_text="Mother NID")
    birth_certificate = serializers.FileField(required=False, help_text="Birth Certificate")
    student_photo = serializers.FileField(required=False, help_text="Student Photo")


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
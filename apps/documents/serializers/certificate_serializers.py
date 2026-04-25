from rest_framework import serializers
from ..models.certificates import CertificateApplication, DocumentAttachment
from apps.students.serializers.management_serializers import StudentManagementSerializer

class DocumentAttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentAttachment
        fields = ['id', 'file_name', 'file', 'uploaded_at']

class CertificateApplicationSerializer(serializers.ModelSerializer):
    student_details = StudentManagementSerializer(source='student', read_only=True)
    attachments = DocumentAttachmentSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = CertificateApplication
        fields = [
            'id', 'student', 'student_details', 'certificate_type', 
            'reason_for_request', 'new_school_name', 'last_class_attended',
            'status', 'status_display', 'admin_notes', 'application_date',
            'reviewed_by', 'reviewed_at', 'attachments', 'timeline_data',
            'generated_certificate'
        ]
        read_only_fields = ['status', 'reviewed_by', 'reviewed_at', 'timeline_data']

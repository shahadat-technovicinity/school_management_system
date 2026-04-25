from django.db import models
from .base import BaseDocument

class CertificateType(models.TextChoices):
    TRANSFER = 'TRANSFER', 'Transfer Certificate (TC)'
    CHARACTER = 'CHARACTER', 'Character Certificate'
    TESTIMONIAL = 'TESTIMONIAL', 'Testimonial'
    BONAFIDE = 'BONAFIDE', 'Bonafide Certificate'

class CertificateApplication(BaseDocument):
    certificate_type = models.CharField(
        max_length=50, 
        choices=CertificateType.choices
    )
    reason_for_request = models.TextField()
    
    # TC Specific Fields (linked to the screenshot requirement)
    new_school_name = models.CharField(max_length=255, blank=True, null=True)
    last_class_attended = models.CharField(max_length=100, blank=True, null=True)
    
    # Document storage for generated file
    generated_certificate = models.FileField(
        upload_to='certificates/issued/%Y/%m/', 
        blank=True, 
        null=True
    )
    
    # Audit log for timeline in UI
    timeline_data = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = 'app_documents_certificates'
        verbose_name = 'Certificate Application'

class DocumentAttachment(models.Model):
    application = models.ForeignKey(
        CertificateApplication, 
        on_delete=models.CASCADE, 
        related_name='attachments'
    )
    file_name = models.CharField(max_length=255)
    file = models.FileField(upload_to='certificates/attachments/%Y/%m/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'app_documents_attachments'

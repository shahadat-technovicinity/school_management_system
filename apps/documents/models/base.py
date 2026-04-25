from django.db import models
from django.conf import settings
from apps.common.models import BaseModel # Assuming common utils exist
import uuid

class DocumentStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending Review'
    APPROVED = 'APPROVED', 'Approved'
    DENIED = 'DENIED', 'Denied'
    ISSUED = 'ISSUED', 'Issued'
    REVOKED = 'REVOKED', 'Revoked'

class BaseDocument(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(
        'students.Student', 
        on_delete=models.CASCADE, 
        related_name="%(class)s_records"
    )
    application_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, 
        choices=DocumentStatus.choices, 
        default=DocumentStatus.PENDING
    )
    admin_notes = models.TextField(blank=True, null=True)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="%(class)s_reviews"
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ['-application_date']

from django.db import models
from django.contrib.auth.models import User

class School_Archive_Document(models.Model):
    # Category choices definition
    CATEGORY_CHOICES = [
        ('student records', 'Student Records'),
        ('academic history', 'Academic History'),
        ('administrative', 'Administrative'),
        ('financial records', 'Financial Records'),
        ('staff records', 'Staff Records'),
    ]

    title = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES) # No extra model needed!
    doc_type = models.CharField(max_length=100) # e.g., PDF, Excel
    file = models.FileField(upload_to='documents/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    tags = models.CharField(max_length=255, blank=True, null=True)  # Comma-separated tags
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
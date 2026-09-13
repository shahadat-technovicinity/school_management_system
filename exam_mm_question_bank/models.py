from django.db import models
from django.core.validators import FileExtensionValidator
from django.conf import settings

# Correct Model Imports
from academic_mm_class_and_section.models import AcademicClass, Section
from academic_create_subject.models import Subject_Name


class QuestionBank(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )

    title = models.CharField(max_length=255)
    
    academic_class = models.ForeignKey(
        AcademicClass, 
        on_delete=models.CASCADE, 
        related_name='question_bank_classes'
    )
    
    # Subject model updated to Subject_Name
    subject = models.ForeignKey(
        Subject_Name, 
        on_delete=models.CASCADE, 
        related_name='question_bank_subjects'
    )
    
    # Multiple Section Selection (ManyToMany)
    sections = models.ManyToManyField(
        Section, 
        related_name='question_bank_sections'
    )
    
    # File upload (PDF, DOC, DOCX)
    file = models.FileField(
        upload_to='question_bank_files/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx'])]
    )
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.academic_class} ({self.status})"
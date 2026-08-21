from django.db import models
from django.conf import settings
from academic_mm_class_and_section.models import AcademicClass, Section



class ExmQuestionBank(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        null=True, 
        blank=True,
    ) 
    
    question_title = models.CharField(max_length=255)
    subject = models.ForeignKey(
        'academic_create_subject.Subject_Name', 
        on_delete=models.CASCADE,
        related_name="examquestionbank"
    )   
    class_name = models.ForeignKey(AcademicClass, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)
    
    # বাই-ডিফল্ট পেন্ডিং থাকবে
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    pdf_file = models.FileField(upload_to='questions_pdfs/', blank=True, null=True)

    def __str__(self):
        user_name = self.uploaded_by.username if self.uploaded_by else 'Anonymous'
        return f"{self.question_title} ({self.class_name}) by {user_name}"
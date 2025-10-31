from django.db import models
from django.conf import settings # Guruttopurno: Eita import kora hoyeche

class ExmQuestionBank(models.Model):
    CLASS_CHOICES = [
        ('class 6', 'Class 6'),
        ('class 7', 'Class 7'),
        ('class 8', 'Class 8'),
        ('class 9', 'Class 9'),
        ('class 10', 'Class 10'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    # ✅ Shongshodhon kora holo: User model-ke settings theke load kora hochche
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    ) 
    
    question_title = models.CharField(max_length=255)
    subject = models.CharField(max_length=100)
    class_name = models.CharField(max_length=20, choices=CLASS_CHOICES)
    date_created = models.DateTimeField(auto_now_add=True)
    
    # default status 'pending' set kora holo
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    pdf_file = models.FileField(upload_to='questions_pdfs/', blank=True, null=True)

    def __str__(self):
        return f"{self.question_title} ({self.class_name}) by {self.uploaded_by.username}"
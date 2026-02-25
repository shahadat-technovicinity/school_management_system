from django.db import models
from django.conf import settings

from student_profile.models import StudentPersonalInfo

class IDCardTemplate(models.Model):
    """
    Stores the design settings (Standard vs Modern shown in UI)
    """
    name = models.CharField(max_length=50) # e.g., "Standard Blue", "Modern Purple"
    template_type = models.CharField(max_length=20, choices=[
        ('standard', 'Standard'),
        ('modern', 'Modern')
    ])
    is_active = models.BooleanField(default=True)
    # You can store color codes or background image paths here
    background_color = models.CharField(max_length=7, default="#ffffff") 

    def __str__(self):
        return self.name

class GeneratedIDCard(models.Model):
    """
    This tracks the history. 
    If a record exists here, the UI shows "Generated". 
    If not, it shows "Not Generated".
    """
    student = models.ForeignKey(StudentPersonalInfo, on_delete=models.CASCADE)
    template = models.ForeignKey(IDCardTemplate, on_delete=models.SET_NULL, null=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    # The actual image file
    card_image = models.ImageField(upload_to='generated_id_cards/')
    
    # Snapshot of data at the time of generation (in case student info changes later)
    snapshot_data = models.JSONField(default=dict) 
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Ensures we only show the latest card for a student in the list
        ordering = ['-created_at']
        unique_together = ['student', 'template'] # Optional: prevent duplicates per template
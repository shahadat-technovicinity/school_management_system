from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

def validate_file_size(value):
    filesize = value.size
    if filesize > 5 * 1024 * 1024: # 5MB limit
        raise ValidationError("Maximum file size is 5MB")

class communication_center_notice(models.Model):
    TYPES = [('general', 'General'), ('co_education', 'Co-education')]

    AUDIENCE_CHOICES = [
        ('all', 'All'),
        ('students', 'All Students'),
        ('staff', 'Students & Staff'),
        ('parents', 'Parents'),
    ]

    PRIORITY_CHOICES = [
        ('new', 'New'),
        ('important', 'Important'),
        ('info', 'Info'),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField()
    notice_type = models.CharField(max_length=20, choices=TYPES)
    target_audience = models.CharField(max_length=100, choices=AUDIENCE_CHOICES, default='all')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='info')
    attachment = models.FileField(upload_to='notices/', validators=[validate_file_size], blank=True, null=True)
    publish_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    

#### Letter Issue Model for Communication Center
class LetterIssue(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
    ]
    PRIORITY_CHOICES = [
        ('normal', 'Normal'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]

    subject = models.CharField(max_length=255)
    reference_number = models.CharField(max_length=100, unique=True)
    addressed_to = models.CharField(max_length=255)
    organization_branch = models.CharField(max_length=255)
    letter_content = models.TextField()
    letter_type = models.CharField(max_length=100) # e.g., Official, Personal
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    attachment = models.FileField(upload_to='letters/', validators=[validate_file_size], blank=True, null=True)
    issue_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reference_number} - {self.subject}"
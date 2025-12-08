from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError


class TeacherAndStaff(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.get_full_name() or self.user.username



def validate_file_size(file):
    max_size_mb = 10
    if file.size > max_size_mb * 1024 * 1024:  # 10MB
        raise ValidationError(f'File size cannot exceed {max_size_mb}MB')

class WorkAssignment(models.Model):
    EMPLOYEE_TYPE_CHOICES = [
        ('teacher', 'Teacher'),
        ('staff', 'Staff'),
    ]
    
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    
    employee_type = models.CharField(max_length=20, choices=EMPLOYEE_TYPE_CHOICES)
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='work_assignments')
    work_title = models.CharField(max_length=255)
    due_date = models.DateField()
    work_description = models.TextField()
    priority_level = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    attachment = models.FileField(
            upload_to='work_attachments/',
            null=True,
            blank=True,
            validators=[
                FileExtensionValidator(
                    allowed_extensions=['pdf', 'doc', 'docx']  
                ),
                validate_file_size  
            ]
    )
    send_notification = models.BooleanField(default=False)
        
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.work_title} - {self.employee.username}"
    
    class Meta:
        ordering = ['-created_at']
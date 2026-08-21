from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from academic_mm_class_and_section.models import AcademicClass, Section



class Top_Student(models.Model):
    # Choice classes for dropdowns

    student_name = models.CharField(max_length=255)
    father_name = models.CharField(max_length=255)
    mother_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    achievement = models.CharField(max_length=255)
    roll = models.PositiveIntegerField()
    
    # Implementing choices here
    student_class = models.ForeignKey(AcademicClass, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    religion = models.CharField(max_length=50)
    village = models.CharField(max_length=255)
    mobile_no = models.CharField(max_length=15)
    photo = models.ImageField(upload_to='student_photos/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        help_text="Upload a later (JPG or PNG, Max 1MB)",
        verbose_name="Later Picture (1080x1080)")
    
    def __str__(self):
        return f"{self.student_name} ({self.roll})"
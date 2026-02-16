from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.utils import timezone
from django.core.validators import FileExtensionValidator


class Top_Student(models.Model):
    # Choice classes for dropdowns
    CLASSCHOICES = [
        ('class 6', 'Class 6'),
        ('class 7', 'Class 7'),
        ('class 8', 'Class 8'),
        ('class 9', 'Class 9'),
        ('class 10', 'Class 10'),]
    
    SECTIONCHOICES = [
        ('section A', 'Section A'),
        ('section B', 'Section B'),
        ('section C', 'Section C'),
        ('section D', 'Section D'),
    ]

    student_name = models.CharField(max_length=255)
    father_name = models.CharField(max_length=255)
    mother_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    achievement = models.CharField(max_length=255)
    roll = models.PositiveIntegerField()
    
    # Implementing choices here
    student_class = models.CharField(max_length=10, choices=CLASSCHOICES, default='class 10')
    section = models.CharField(max_length=10, choices=SECTIONCHOICES, default='section A')
    subject = models.CharField(max_length=100)
    religion = models.CharField(max_length=50)
    village = models.CharField(max_length=255)
    mobile_no = models.CharField(max_length=15)
    photo = models.ImageField(upload_to='student_photos/', null=True, blank=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        help_text="Upload a later (JPG or PNG, Max 1MB)",
        verbose_name="Later Picture (1080x1080)")

    def __str__(self):
        return f"{self.student_name} ({self.roll})"
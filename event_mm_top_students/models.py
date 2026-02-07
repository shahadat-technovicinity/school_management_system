from django.db import models

class StudentTop(models.Model):
    CLASS_NAME_CHOICES = [
        ('6', '6'),
        ('7', '7'),
        ('8', '8'),
        ('9', '9'),
        ('10', '10')]
    SECTION_CHOICES = [
        ('section A', 'Section A'),
        ('section B', 'Section B'),
        ('section C', 'Section C'),
        ('section D', 'Section D')]
    # Basic Info
    student_name = models.CharField(max_length=255)
    father_name = models.CharField(max_length=255)
    mother_name = models.CharField(max_length=255)
    date_of_birth = models.DateField()
    roll = models.IntegerField(unique=True)
    
    # Categorization
    class_name = models.CharField(max_length=50, choices=CLASS_NAME_CHOICES) # Eg: 10, 9
    section = models.CharField(max_length=10, choices=SECTION_CHOICES)   # Eg: A, B, C
    subject = models.CharField(max_length=100)
    achievement = models.CharField(max_length=255)
    
    # Personal Info
    religion = models.CharField(max_length=50)
    village = models.CharField(max_length=255)
    mobile_no = models.CharField(max_length=15)
    photo = models.ImageField(upload_to='students/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name} (Roll: {self.roll})"
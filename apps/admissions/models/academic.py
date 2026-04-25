from django.db import models
from apps.admissions.models import StudentAdmission

class PreviousAcademicRecord(models.Model):
    admission = models.OneToOneField(StudentAdmission, on_delete=models.CASCADE, related_name='previous_academic_record')
    school_name = models.CharField(max_length=255)
    school_address = models.CharField(max_length=500, blank=True, null=True)
    class_studying_in = models.CharField(max_length=50, blank=True, null=True)
    roll_number = models.CharField(max_length=50, blank=True, null=True)
    gpa_obtained = models.CharField(max_length=10, blank=True, null=True)
    passing_year = models.CharField(max_length=4, blank=True, null=True)
    
    def __str__(self):
        return f"{self.school_name} - {self.admission.application_number}"

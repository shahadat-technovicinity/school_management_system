from django.db import models
from student_admission.models import StudentAdmission

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

class AdmissionSkill(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class AdmissionSkillLink(models.Model):
    admission = models.ForeignKey(StudentAdmission, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(AdmissionSkill, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('admission', 'skill')

class LotterySession(models.Model):
    academic_year = models.ForeignKey('academics.AcademicYear', on_delete=models.CASCADE, related_name='lottery_sessions')
    target_class = models.CharField(max_length=100) # Choices
    total_seats = models.PositiveIntegerField()
    lottery_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Lottery {self.target_class} ({self.academic_year})"


class AdmissionDocument(models.Model):
    admission = models.ForeignKey(StudentAdmission, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50) # TC, Mother_NID, Birth_Certificate, Student_Photo
    file = models.FileField(upload_to='admission_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.document_type} for {self.admission.application_number}"

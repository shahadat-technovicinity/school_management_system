from django.db import models
from apps.admissions.models import StudentAdmission

class AdmissionDocument(models.Model):
    admission = models.ForeignKey(StudentAdmission, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=50) # TC, Mother_NID, Birth_Certificate, Student_Photo
    file = models.FileField(upload_to='admission_documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.document_type} for {self.admission.application_number}"

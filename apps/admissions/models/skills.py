from django.db import models
from apps.admissions.models import StudentAdmission

class AdmissionSkill(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class AdmissionSkillLink(models.Model):
    admission = models.ForeignKey(StudentAdmission, on_delete=models.CASCADE, related_name='skills')
    skill = models.ForeignKey(AdmissionSkill, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('admission', 'skill')

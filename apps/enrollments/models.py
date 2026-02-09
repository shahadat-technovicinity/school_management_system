from django.db import models

from apps.academics.models import ClassSection, AcademicYear
from student_profile.models import StudentPersonalInfo

class Enrollment(models.Model):
    student = models.ForeignKey(StudentPersonalInfo, on_delete=models.CASCADE)
    class_section = models.ForeignKey(ClassSection, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    roll_no = models.PositiveIntegerField()

    class Meta:
        unique_together = ('student', 'academic_year')

    def __str__(self):
        return f"{self.student} → {self.class_section}"

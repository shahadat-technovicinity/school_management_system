from django.db import models

from apps.academics.models import ClassSection, AcademicYear
from apps.students.models import Student
from academic_mm_class_and_section.models import AcademicClass, Section

class Enrollment(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    # class_section = models.ForeignKey(ClassSection, on_delete=models.CASCADE)
    # academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    classname = models.ForeignKey(AcademicClass, on_delete=models.PROTECT)
    section = models.ForeignKey(Section, on_delete=models.PROTECT)
    academic_year = models.CharField(max_length=20)
    roll_no = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        unique_together = ('student', 'academic_year')

    

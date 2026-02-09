from django.db import models

from academic_class_routine.models import Teacher
from apps.academics.models import ClassSection
from student_profile.models import StudentPersonalInfo

class Attendance(models.Model):
    PRESENT = 'P'
    ABSENT = 'A'

    STATUS_CHOICES = [
        (PRESENT, 'Present'),
        (ABSENT, 'Absent'),
    ]

    student = models.ForeignKey(StudentPersonalInfo, on_delete=models.CASCADE)
    class_section = models.ForeignKey(ClassSection, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    marked_by = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL, null=True
    )

    class Meta:
        unique_together = ('student', 'class_section', 'date')
        indexes = [
            models.Index(fields=['class_section', 'date']),
            models.Index(fields=['student', 'date']),
        ]

    def __str__(self):
        return f"{self.student} {self.date} {self.status}"

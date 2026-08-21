from django.db import models

# from academic_class_routine.models import Teacher
# from teacher_mm_teacher.models import Teacher
from django.conf import settings

# from apps.academics.models import ClassSection
from apps.students.models import Student
from academic_mm_class_and_section.models import AcademicClass, Section

class Attendance(models.Model):
    PRESENT = 'P'
    ABSENT = 'A'

    STATUS_CHOICES = [
        (PRESENT, 'Present'),
        (ABSENT, 'Absent'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    # class_section = models.ForeignKey(ClassSection, on_delete=models.CASCADE)
    classname = models.ForeignKey(AcademicClass, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    marked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'role__name': 'Teacher'}
    )

    class Meta:
        unique_together = ('student', 'classname', 'section', 'date')
        indexes = [
            models.Index(fields=['classname', 'section', 'date']),
            models.Index(fields=['student', 'date']),
        ]

    def __str__(self):
        return f"{self.student} {self.date} {self.status}"

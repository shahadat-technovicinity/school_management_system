from django.db import models
from academic_mm_class_and_section.models import AcademicClass, Section

class ExamName(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ExamSetup(models.Model):
    SHIFT_CHOICES = [
        ('morning', 'Morning'),
        ('day', 'Day'),
    ]

    exam_name = models.ForeignKey(
        ExamName, 
        on_delete=models.CASCADE, 
        related_name='exam_setups'
    )
    academic_class = models.ForeignKey(
        AcademicClass, 
        on_delete=models.CASCADE, 
        related_name='exam_setups'
    )
    sections = models.ManyToManyField(
        Section, 
        related_name='exam_setups'
    )
    shift = models.CharField(max_length=10, choices=SHIFT_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.exam_name.name} - {self.academic_class.name} ({self.shift})"
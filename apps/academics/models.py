from django.db import models

from academic_class_routine.models import Teacher

class AcademicYear(models.Model):
    year_label = models.CharField(max_length=20, unique=True)  # 2025-2026
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.year_label

class Class(models.Model):
    name = models.CharField(max_length=20)      # Class 5
    level = models.PositiveIntegerField(unique=True)

    def __str__(self):
        return self.name

class Section(models.Model):
    name = models.CharField(max_length=5)  # A, B, C

    def __str__(self):
        return self.name


class ClassSection(models.Model):
    class_room = models.ForeignKey(Class, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)
    academic_year = models.ForeignKey(AcademicYear, on_delete=models.CASCADE)
    class_teacher = models.ForeignKey(
        Teacher, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        unique_together = ('class_room', 'section', 'academic_year')

    def __str__(self):
        return f"{self.class_room} {self.section} ({self.academic_year})"

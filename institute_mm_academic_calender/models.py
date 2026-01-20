from django.db import models

class AcademicCalendar(models.Model):
    # Figma-r 'Select Academic Year' ongsho
    year_start = models.DateField()
    year_end = models.DateField()
    academic_year_label = models.CharField(max_length=20) # e.g., "2025-2026"

    class Meta:
        verbose_name_plural = "Academic Calendars"

class Holiday(models.Model):
    # Figma-r 'Holiday Type' er choices
    TYPE_CHOICES = [
        ('academic', 'Academic Holiday'),
        ('national', 'National Holiday'),
        ('religious', 'Religious Holiday'),
        ('other', 'Other Holiday'),
    ]

    holiday_name = models.CharField(max_length=255) # Figma: 'Holiday Name'
    start_date = models.DateField() # Figma: 'Start Date'
    end_date = models.DateField()   # Figma: 'End Date'
    holiday_type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    def __str__(self):
        return self.holiday_name
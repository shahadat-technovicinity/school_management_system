from django.db import models

# Create your models here.
class Exam(models.Model):
    VISIBILITY_CHOICES = [
        ("public", "Public"),
        ("private", "Private"),
    ]

    exam_title = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    total_points = models.PositiveIntegerField(default=100)
    description = models.TextField(blank=True)
    exam_date = models.DateField(null=True, blank=True)

    # Time settings
    duration = models.DurationField(help_text="Total duration of the exam (HH:MM:SS).")
    available_from = models.DateTimeField(null=True, blank=True)
    available_until = models.DateTimeField(null=True, blank=True)
    time_zone = models.CharField(max_length=64, default="UTC")

    visibility = models.CharField(max_length=7, choices=VISIBILITY_CHOICES, default="public")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.exam_title} ({self.subject})"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.available_from and self.available_until:
            if self.available_until <= self.available_from:
                raise ValidationError({"available_until": "Available until must be after available from."})

        if self.duration is not None and self.duration.total_seconds() <= 0:
            raise ValidationError({"duration": "Duration must be greater than 0."})


class ExamRoutine(models.Model):
    EXAM_TYPE_CHOICES = [
        ("midterm", "Midterm"),
        ("final", "Final"),
        ("term", "Term Exam"),
        ("assessment", "Assessment"),
        ("other", "Other"),
    ]

    SHIFT_CHOICES = [
        ("morning", "Morning"),
        ("day", "Day"),
        ("evening", "Evening"),
    ]

    STREAM_CHOICES = [
        ("science", "Science"),
        ("arts", "Arts"),
        ("commerce", "Commerce"),
    ]

    title = models.CharField(max_length=255)
    exam_type = models.CharField(max_length=20, choices=EXAM_TYPE_CHOICES)
    academic_year = models.PositiveIntegerField(help_text="e.g., 2025")
    start_date = models.DateField()
    end_date = models.DateField()
    class_selection = models.CharField(max_length=100, help_text="e.g., Class 10")
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES)
    stream = models.CharField(max_length=20, choices=STREAM_CHOICES, blank=True, null=True, help_text="Optional stream scope for this routine")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.academic_year} ({self.class_selection})"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "End date must be on or after start date."})


class ExamRoutineItem(models.Model):
    STREAM_CHOICES = [
        ("science", "Science"),
        ("arts", "Arts"),
        ("commerce", "Commerce"),
    ]

    routine = models.ForeignKey(ExamRoutine, on_delete=models.CASCADE, related_name="items")
    date = models.DateField()
    # Day can be derived from date; store for convenience if needed
    day = models.CharField(max_length=20, blank=True, help_text="Optional, will often be derived from date")
    start_time = models.TimeField()
    end_time = models.TimeField()
    subject = models.CharField(max_length=200)
    exam_hall = models.CharField(max_length=100, blank=True)
    stream = models.CharField(max_length=20, choices=STREAM_CHOICES, blank=True, null=True)

    class Meta:
        ordering = ["date", "start_time"]
        verbose_name = "Exam Routine Item"
        verbose_name_plural = "Exam Routine Items"

    def __str__(self):
        return f"{self.subject} on {self.date} ({self.start_time} - {self.end_time})"

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.end_time and self.start_time and self.end_time <= self.start_time:
            raise ValidationError({"end_time": "End time must be after start time."})

        if self.routine_id:
            # Ensure date is within routine date range
            if (self.routine.start_date and self.date < self.routine.start_date) or (
                self.routine.end_date and self.date > self.routine.end_date
            ):
                raise ValidationError({"date": "Item date must be within the routine's start and end dates."})
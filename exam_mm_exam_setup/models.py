from django.db import models
from django.core.exceptions import ValidationError


class exm_mm_exam_setup(models.Model):
    VISIBILITY_CHOICES = [
        ("public", "Public"),
        ("private", "Private"),
    ]

    exam_title = models.CharField(max_length=200)
    
    # academic_create_subject অ্যাপের Subject_Name মডেলের সাথে রিলেশন
    subject = models.ForeignKey(
        'academic_create_subject.Subject_Name', 
        on_delete=models.CASCADE,
        related_name="exams"
    )
    
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
        return f"{self.exam_title} ({self.subject.name if self.subject else 'No Subject'})"

    def clean(self):
        if self.available_from and self.available_until:
            if self.available_until <= self.available_from:
                raise ValidationError({"available_until": "Available until must be after available from."})

        if self.duration is not None and self.duration.total_seconds() <= 0:
            raise ValidationError({"duration": "Duration must be greater than 0."})
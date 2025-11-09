from django.db import models
from student_profile.models import StudentPersonalInfo


class ExamMark(models.Model):
    EXAM_TYPES = [
        ('mid', 'Mid-term Examination'),
        ('final', 'Final Examination'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('saved', 'Saved'),
        ('pending', 'Pending'),
        ('failed', 'Failed'),
    ]

    student = models.ForeignKey(StudentPersonalInfo, on_delete=models.CASCADE)
    subject = models.CharField(max_length=100)
    exam_type = models.CharField(max_length=10, choices=EXAM_TYPES)
    writing = models.IntegerField(default=0)
    practical = models.IntegerField(default=0)
    mcq = models.IntegerField(default=0)
    total = models.IntegerField(editable=False, default=0)  # auto calculate
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Automatically calculate total before saving
        self.total = (self.writing or 0) + (self.practical or 0) + (self.mcq or 0)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.first_name} {self.student.last_name} - {self.subject} ({self.exam_type})"

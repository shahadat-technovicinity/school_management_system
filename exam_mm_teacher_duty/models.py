from django.db import models
from django.conf import settings
from academic_create_subject.models import Subject_Name


STATUS_CHOICES = [
    ('Pending', 'Pending'),
    ('Confirmed', 'Confirmed'),
    ('Conflict', 'Conflict'),
]


class ExamDuty(models.Model):
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='exam_duties',
    )
    subject = models.ForeignKey(
        Subject_Name,
        on_delete=models.PROTECT,
        related_name='exam_duties'
    )
    exam_date = models.DateField()
    time_slot = models.CharField(max_length=50)
    room_number = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    send_notification = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-exam_date']

    def __str__(self):
        return f"{self.teacher} - {self.subject} ({self.exam_date})"
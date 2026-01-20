from django.db import models

class student_admission_exam(models.Model):
    EXAM_STATUS_CHOICES = (
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('postponed', 'Postponed'),
        ('cancelled', 'Cancelled'),
    )

    NOTIFICATION_CHOICES = (
        ('sms', 'SMS'),
        ('email', 'Email'),
        ('whatsapp', 'Whatsapp'),
        ('whatsapp & sms', 'Whatsapp & SMS'),

    )
    
    exam_name = models.CharField(max_length=255)
    exam_date = models.DateField()
    exam_time = models.TimeField()
    venue = models.CharField(max_length=255)
    exam_status = models.CharField(max_length=50, choices=EXAM_STATUS_CHOICES, default='scheduled')
    notify_parents = models.BooleanField(default=False)
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_CHOICES, default='whatsapp_sms')
    
    def __str__(self):
        return f"{self.exam_name} ({self.status})"

    class Meta:
        verbose_name = "Exam"
        verbose_name_plural = "Exams"
        ordering = ['-exam_date', '-exam_time']
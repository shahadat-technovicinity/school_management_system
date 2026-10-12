from django.db import models
from apps.students.models import Student

from communication_canter_sms_template.models import SMSTemplate


class SMSHistory(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    )

    student = models.ForeignKey(
        Student, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='sms_histories'
    )
    template = models.ForeignKey(
        SMSTemplate, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='sms_histories'
    )
    phone_number = models.CharField(max_length=20)
    message = models.TextField()
    request_id = models.CharField(max_length=100, null=True, blank=True, help_text="sms.net.bd Request ID")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    error_message = models.TextField(null=True, blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent_at']
        verbose_name_plural = "SMS Histories"

    def __str__(self):
        return f"{self.phone_number} - {self.status} - {self.sent_at.strftime('%Y-%m-%d %H:%M')}"
from django.db import models
from apps.students.models import Student


class SMSTemplate(models.Model):
    title = models.CharField(max_length=100, help_text="টেমপ্লেটের নাম (যেমন: ফি রসিদ, নোটিশ)")
    content_id = models.CharField(max_length=50, blank=True, null=True, help_text="sms.net.bd Content ID (যদি থাকে)")
    message_body = models.TextField(help_text="মেসেজের মূল টেক্সট")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


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
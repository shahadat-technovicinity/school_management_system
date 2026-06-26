from django.db import models
from django.conf import settings  # ১. এটি ইম্পোর্ট করুন

class Mail(models.Model):
    FOLDER_CHOICES = [
        ('inbox',    'Inbox'),
        ('sent',     'Sent'),
        ('draft',    'Draft'),
        ('trash',    'Trash'),
        ('parents',  'Parents'),
        ('teachers', 'Teachers'),
    ]

    # ২. User এর বদলে settings.AUTH_USER_MODEL ব্যবহার করুন
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='sent_mails', 
        on_delete=models.CASCADE
    )
    to_emails  = models.TextField(help_text='Comma-separated email addresses, e.g. a@b.com, c@d.com')
    subject    = models.CharField(max_length=255)
    body       = models.TextField()
    folder     = models.CharField(max_length=20, choices=FOLDER_CHOICES, default='inbox')
    is_read    = models.BooleanField(default=False)
    is_starred = models.BooleanField(default=False)
    reply_to   = models.ForeignKey(
        'self', null=True, blank=True,
        related_name='replies', on_delete=models.SET_NULL
    )
    smtp_sent  = models.BooleanField(default=False)
    smtp_error = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.folder}] {self.subject}"


class Attachment(models.Model):
    mail        = models.ForeignKey(Mail, related_name='attachments', on_delete=models.CASCADE)
    file        = models.FileField(upload_to='attachments/%Y/%m/%d/')
    filename    = models.CharField(max_length=255)
    file_size   = models.PositiveIntegerField(default=0)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename
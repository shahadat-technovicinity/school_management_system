from django.db import models

# Create your models here.

class academiconlineclass(models.Model):
    CLASS_CHOICES = (
            ('Class 6', 'classs 6'),
            ('Class 7', 'class 7'),
            ('Class 8', 'class 8'),
            ('Class 9', 'class 9'),
            ('Class 10', 'class 10'),
        )
    
    SECTION_CHOICES = (
            ('Section A', 'section A'),
            ('Section B', 'section B'),
            ('Section C', 'section C'),
            ('Section D', 'section D')
        )
    
    NOTIFICATION_CHOICES = (
            ('Whatsapp & SMS', 'whatsapp & sms'),
            ('Whatsapp Only', 'whatsapp only'),
            ('SMS Only', 'sms only'),
            ('Email', 'email')
        )

    For_Class = models.CharField(max_length=50, choices=CLASS_CHOICES, default='Class 6')
    Section = models.CharField(max_length= 50, choices=SECTION_CHOICES)
    Class_Topic = models.CharField(max_length=255)
    Class_Date = models.DateField()
    Class_Time = models.TimeField()
    Password = models.CharField(max_length=255)
    notify_parents = models.BooleanField(default=False)
    Notification_Type = models.CharField(max_length=50, choices=NOTIFICATION_CHOICES)


    def __str__(self):
        return f"{self.Class_Topic} ({self.Password})"

    class Meta:
        verbose_name = "Class_Topic"
        verbose_name_plural = "Class_Topics"

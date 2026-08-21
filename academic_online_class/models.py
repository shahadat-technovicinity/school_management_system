from django.db import models
from academic_mm_class_and_section.models import AcademicClass, Section

# Create your models here.

class academiconlineclass(models.Model):
    
    NOTIFICATION_CHOICES = (
            ('Whatsapp & SMS', 'whatsapp & sms'),
            ('Whatsapp Only', 'whatsapp only'),
            ('SMS Only', 'sms only'),
            ('Email', 'email')
        )

    For_Class = models.ForeignKey(AcademicClass, on_delete=models.PROTECT)
    Section = models.ForeignKey(Section, on_delete=models.PROTECT)
    Class_Topic = models.CharField(max_length=255)
    Class_Date = models.DateField()
    Class_Time = models.TimeField()
    Password = models.CharField(max_length=255, blank=True, null=True)
    Class_Link = models.URLField(max_length=500, blank=True, null=True)
    notify_parents = models.BooleanField(default=False)
    Notification_Type = models.CharField(max_length=50, choices=NOTIFICATION_CHOICES)


    def __str__(self):
        return f"{self.Class_Topic} ({self.Password})"

    class Meta:
        verbose_name = "Class_Topic"
        verbose_name_plural = "Class_Topics"




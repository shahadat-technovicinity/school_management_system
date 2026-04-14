from django.db import models

class SMSTemplate(models.Model):
    CATEGORY_CHOICES = [
        ('Attendance', 'Attendance'),
        ('Fees', 'Fees'),
        ('Exam', 'Exam'),
        ('Event', 'Event'),
        ('Notice', 'General Notice'),
        ('Admission', 'Admission'),
        ('Result', 'Result'),
        ('Holiday', 'Holiday'),
    ]

    template_name = models.CharField(max_length=255)
    category = models.CharField(
        max_length=50, 
        choices=CATEGORY_CHOICES, 
        default='Notice'
    )
    template_content = models.TextField()
    last_edited = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-last_edited']

    def __str__(self):
        return f"{self.template_name} ({self.category})"
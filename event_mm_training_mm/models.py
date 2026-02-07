from django.db import models

class TrainingRecord(models.Model):
    STATUS_CHOICES = [
        ('Completed', 'Completed'),
        ('Upcoming', 'Upcoming'),
    ]

    teacher_id = models.CharField(max_length=50) # Eg: T-2025-0042
    teacher_name = models.CharField(max_length=255)
    training_name = models.CharField(max_length=255)
    venue = models.CharField(max_length=255)
    date_to = models.DateField()
    total_days = models.IntegerField()
    authority = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Upcoming')
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.training_name} - {self.teacher_name}"
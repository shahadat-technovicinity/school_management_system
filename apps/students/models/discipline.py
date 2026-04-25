from django.db import models
from .core import Student

class StudentDiscipline(models.Model):
    LEVEL_CHOICES = [
        ('low', 'Low (Warning)'),
        ('medium', 'Medium (Suspension)'),
        ('high', 'High (Expulsion)'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='disciplinary_records')
    incident_date = models.DateField()
    title = models.CharField(max_length=255) # e.g., "Late Submission", "Disruptive Behavior"
    description = models.TextField()
    action_taken = models.CharField(max_length=255) # e.g., "Verbal Warning", "Parent Notified"
    severity = models.CharField(max_length=10, choices=LEVEL_CHOICES, default='low')
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-incident_date']
        db_table = 'student_discipline_records'

    def __str__(self):
        return f"{self.student.full_name} - {self.title}"

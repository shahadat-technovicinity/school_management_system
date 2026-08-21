from django.db import models
from academic_mm_class_and_section.models import AcademicClass, Section

class LotterySession(models.Model):
    # academic_year = models.ForeignKey('academics.AcademicYear', on_delete=models.CASCADE, related_name='lottery_sessions')
    academic_year = models.CharField(max_length=100) # Choices
    target_class = models.ForeignKey(AcademicClass, on_delete=models.PROTECT)
    total_seats = models.PositiveIntegerField()
    lottery_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Lottery {self.target_class} ({self.academic_year})"

from django.db import models

class LotterySession(models.Model):
    academic_year = models.ForeignKey('academics.AcademicYear', on_delete=models.CASCADE, related_name='lottery_sessions')
    target_class = models.CharField(max_length=100) # Choices
    total_seats = models.PositiveIntegerField()
    lottery_date = models.DateField()
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Lottery {self.target_class} ({self.academic_year})"

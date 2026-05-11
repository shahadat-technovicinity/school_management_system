from django.db import models


class CrimeReport(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('pending', 'Pending'),
        ('closed', 'Closed'),
    ]

    case_number = models.CharField(max_length=50, unique=True, blank=True)
    plaintiff = models.CharField(max_length=255)
    defendant = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    date_filed = models.DateField()
    progress_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_filed']

    def save(self, *args, **kwargs):
        if not self.case_number:
            from django.utils import timezone
            year = timezone.now().year
            count = CrimeReport.objects.filter(
                date_filed__year=year
            ).count() + 1
            self.case_number = f"CASE-{year}-{str(count).zfill(3)}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.case_number} - {self.subject}"
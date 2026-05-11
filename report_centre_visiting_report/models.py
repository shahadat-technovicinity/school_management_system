from django.db import models


class VisitingReport(models.Model):
    officer_name = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    office = models.CharField(max_length=255)
    visit_date = models.DateField()
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-visit_date']

    def __str__(self):
        return f"{self.officer_name} - {self.visit_date}"
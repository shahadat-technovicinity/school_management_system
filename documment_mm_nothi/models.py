from django.db import models

class Nothi(models.Model):
    nothi_no = models.CharField(max_length=50, unique=True, blank=True, null=True)
    title = models.CharField(max_length=255)  # e.g. Testimonial (2024-2025)
    academic_year = models.CharField(max_length=20, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.nothi_no:
            last_nothi = Nothi.objects.all().order_by('id').last()
            last_id = last_nothi.id if last_nothi else 0
            self.nothi_no = f"NTH-{last_id + 1:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nothi_no} - {self.title}"





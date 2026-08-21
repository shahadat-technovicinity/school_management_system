from django.db import models

class AcademicClass(models.Model):
    name = models.CharField(max_length=100, unique=True)  # e.g., "Class 6"
    numeric_value = models.IntegerField(unique=True)     # e.g., 6
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Section(models.Model):
    name = models.CharField(max_length=50, unique=True)   # e.g., "Section A" or "A"
    status = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
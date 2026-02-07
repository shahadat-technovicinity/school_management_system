from django.db import models
from django.conf import settings

class TeacherDiary(models.Model):
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    class_name = models.CharField(max_length=100)
    subject = models.CharField(max_length=100)
    date = models.DateField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date'] 

    def __str__(self):
        return self.title
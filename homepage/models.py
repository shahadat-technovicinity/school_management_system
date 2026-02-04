from django.db import models

class Home_Page_Slider(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    image = models.ImageField(upload_to='sliders/')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title if self.title else f"Slider {self.id}"
    


# Message Model
class Message(models.Model):
    MESSAGE_TYPES = (
        ('president', 'সভাপতি মহোদয়ের বাণী'),
        ('principal', 'প্রধান শিক্ষক মহোদয়ের বাণী'),
    )
    
    title = models.CharField(max_length=200, blank=True, null=True)
    type = models.CharField(max_length=20, choices=MESSAGE_TYPES, unique=True)
    content = models.TextField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
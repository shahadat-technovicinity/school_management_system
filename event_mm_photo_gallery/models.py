from django.db import models

class PhotoGallery(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='gallery/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    



class VideoGallery(models.Model):
    video_title = models.CharField(max_length=255)
    poster_image = models.ImageField(upload_to='video_posters/')
    video_url = models.URLField()  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.video_title
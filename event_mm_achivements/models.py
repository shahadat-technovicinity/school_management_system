from django.db import models

class Event_mm_Achievement(models.Model):
    CATEGORY_CHOICES = [
        ('Academic', 'Academic'),
        ('Sports', 'Sports'),
        ('Arts & Culture', 'Arts & Culture'),
    ]

    title = models.CharField(max_length=255)
    date_achieved = models.DateField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    students_involved = models.TextField(help_text="Enter names separated by commas")
    image = models.ImageField(upload_to='achievements/', null=True, blank=True)
    is_published = models.BooleanField(default=False) # Modal-er "Publish immediately" toggle
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
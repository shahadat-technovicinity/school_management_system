from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.contrib.auth.models import User 
from django.conf import settings


class MagazineIssue(models.Model):
    STATUS_CHOICES = [
        ('Draft', 'Draft'),
        ('Under Review', 'Under Review'),
        ('Published', 'Published'),
    ]

    title = models.CharField(max_length=255)
    issue_number = models.CharField(max_length=100)
    publication_date = models.DateField(null=True, blank=True)
    editor_in_chief = models.CharField(max_length=255) 
    overview = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Draft')
    cover_image = models.ImageField(upload_to='magazine_covers/',
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        help_text="Upload a cover image (JPG or PNG, Max 1MB)",
        verbose_name="Cover Image (1080x1080)")
    keywords = models.CharField(max_length=500, help_text="Comma separated keywords")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.issue_number}"
    

### Scheduled Publication Model for Magazine Issues ###
class ScheduledPublication(models.Model):
    magazine_title = models.CharField(max_length=255)
    issue_number = models.CharField(max_length=100)
    target_publication_date = models.DateField()
    
    editor_assigned = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='editor_tasks'
    )
    
    publication_description = models.TextField(blank=True, null=True)
    
    team_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, 
        related_name='team_tasks'
    )
    
    content_submission_deadline = models.DateField()
    review_deadline = models.DateField()
    initial_content_plan = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.magazine_title
    


### Content Submission Model linked to Scheduled Publication ###
class ContentSubmission(models.Model):
    CATEGORY_CHOICES = [
        ('news', 'News'),
        ('feature', 'Feature'),
        ('interview', 'Interview'),
        ('opinion', 'Opinion'),
    ]

    article_title = models.CharField(max_length=255)
    
    # Phase 2 এর মডেলের সাথে লিঙ্ক
    target_publication = models.ForeignKey(
        'ScheduledPublication', 
        on_delete=models.CASCADE, 
        related_name='contents'
    )
    
    author_name = models.CharField(max_length=255)
    content_category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    content_summary = models.TextField()
    
    # ফাইল আপলোডের জন্য
    uploaded_file = models.FileField(upload_to='submissions/%Y/%m/%d/')
    
    status = models.CharField(
        max_length=20, 
        choices=[('Draft', 'Draft'), ('Review', 'Under Review')], 
        default='Draft'
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.article_title
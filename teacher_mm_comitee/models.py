# committees/models.py
from django.db import models

class CommitteeMember(models.Model):
    COMMITTEE_CHOICES = [
        ('PTA', 'PTA Committee'),
        ('MMC', 'MMC Committee'),
        ('CABINET', 'Cabinet Committee'),
    ]
    
    POSITION_CHOICES = [
        ('Chairperson', 'Chairperson'),
        ('Vice Chairperson', 'Vice Chairperson'),
        ('Secretary', 'Secretary'),
        ('Treasurer', 'Treasurer'),
        ('Member', 'Member'),
    ]
    
    # Basic Info
    full_name = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    avatar = models.ImageField(upload_to='member_avatars/', null=True, blank=True)  # এইটা যোগ করলাম
    
    # Committee Info
    committee_type = models.CharField(max_length=20, choices=COMMITTEE_CHOICES, default='PTA')
    position = models.CharField(max_length=50, choices=POSITION_CHOICES)
    
    # Term Info
    term_start = models.DateField()
    term_end = models.DateField()
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.full_name} - {self.committee_type}"
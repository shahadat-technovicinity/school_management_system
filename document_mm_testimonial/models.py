from django.db import models

class StudentApplication(models.Model):
    BOARD_CHOICES = [
        ('রাজশাহী শিক্ষাবোর্ড', 'রাজশাহী শিক্ষাবোর্ড'),
        ('কারিগরি শিক্ষাবোর্ড', 'কারিগরি শিক্ষাবোর্ড'),
    ]

    DEPARTMENT_CHOICES = [
        ('মানবিক', 'মানবিক'),
        ('বিজ্ঞান', 'বিজ্ঞান'),
        ('এপারেল ম্যানুফেকচারিং বেসিকস', 'এপারেল ম্যানুফেকচারিং বেসিকস'),
        ('ফুড প্রসেসিং এন্ড প্রিজার্ভেশন', 'ফুড প্রসেসিং এন্ড প্রিজার্ভেশন'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    student_name_bn = models.CharField(max_length=255)
    date_of_birth = models.CharField(max_length=50)       # e.g., "২৪-০৮-২০০৪"
    father_name_bn = models.CharField(max_length=255)
    mother_name_bn = models.CharField(max_length=255)
    village = models.CharField(max_length=255)
    post_office = models.CharField(max_length=100)
    upazila = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    passing_year = models.CharField(max_length=10)       # e.g., "২০২০"
    exam_month = models.CharField(max_length=50)        # e.g., "ফেব্রুয়ারী"
    board = models.CharField(max_length=100, choices=BOARD_CHOICES)
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES)
    gpa = models.CharField(max_length=10)                # e.g., "৫.০০"
    roll = models.CharField(max_length=50)               # e.g., "১৭০৩৭০"
    registration_no = models.CharField(max_length=50)    # e.g., "১৭১২৮৫৫৬৬২"
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name_bn} - {self.roll} ({self.status})"
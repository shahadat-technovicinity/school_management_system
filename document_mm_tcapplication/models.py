from django.db import models

class TCApplication(models.Model):
    REASON_CHOICES = [
        ('অভিভাবকের অভিপ্রায়', 'অভিভাবকের অভিপ্রায়'),
        ('বাসস্থান পরিবর্তন', 'বাসস্থান পরিবর্তন'),
        ('শারীরিক অসুস্থতা', 'শারীরিক অসুস্থতা'),
        ('অন্যান্য', 'অন্যান্য'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    serial_no = models.CharField(max_length=50, blank=True, null=True)
    issue_date = models.DateField(auto_now_add=True)
    
    # Student Info
    student_name_bn = models.CharField(max_length=255)
    father_name_bn = models.CharField(max_length=255)
    mother_name_bn = models.CharField(max_length=255)
    village = models.CharField(max_length=255)
    post_office = models.CharField(max_length=100)
    upazila = models.CharField(max_length=100, default='ব্রাহ্মণবাড়িয়া সদর')
    district = models.CharField(max_length=100, default='ব্রাহ্মণবাড়িয়া')
    
    # Leaving & Age Details
    leaving_date = models.DateField()
    date_of_birth = models.DateField()
    age_years = models.CharField(max_length=10)
    age_months = models.CharField(max_length=10)
    age_days = models.CharField(max_length=10)
    
    # Academic Details
    current_class = models.CharField(max_length=100)
    promoted_from_class = models.CharField(max_length=100)
    promoted_to_class = models.CharField(max_length=100)
    is_promoted = models.BooleanField(default=True)  # উত্তীর্ণ হয়েছে / হয় নাই
    fees_paid_up_to_year = models.CharField(max_length=10)
    registration_no = models.CharField(max_length=100, blank=True, null=True)
    
    # Reason
    leaving_reason = models.CharField(max_length=100, choices=REASON_CHOICES, default='অভিভাবকের অভিপ্রায়')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.serial_no:
            self.serial_no = f"TC-{self.id:04d}"
            super().save(update_fields=['serial_no'])

    def __str__(self):
        return f"{self.student_name_bn} - {self.serial_no} ({self.status})"
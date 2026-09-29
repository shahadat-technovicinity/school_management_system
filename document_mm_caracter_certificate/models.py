from django.db import models

class CharacterCertificateApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    GROUP_CHOICES = [
        ('বিজ্ঞান', 'বিজ্ঞান'),
        ('মানবিক', 'মানবিক'),
        ('ব্যবসায় শিক্ষা', 'ব্যবসায় শিক্ষা'),
        ('সাধারণ', 'সাধারণ'),
    ]

    serial_no = models.CharField(max_length=50, blank=True, null=True)
    issue_date = models.DateField(auto_now_add=True)
    
    # Student Info
    student_name_bn = models.CharField(max_length=255)
    father_name_bn = models.CharField(max_length=255)
    mother_name_bn = models.CharField(max_length=255)
    village = models.CharField(max_length=255)
    post_office = models.CharField(max_length=100)
    upazila = models.CharField(max_length=100, default='নবীনগর')
    district = models.CharField(max_length=100, default='ব্রাহ্মণবাড়িয়া')
    school_name_bn = models.CharField(max_length=255, default='অত্র বিদ্যালয়')
    
    # Academic Details
    academic_year = models.CharField(max_length=20, help_text="যেমন: ২০০৩/২০২৩")
    admission_date = models.DateField()
    admission_class = models.CharField(max_length=100, default="ষষ্ঠ")
    passing_year = models.CharField(max_length=10, help_text="যেমন: ২০০৮/২০২৪")
    exam_group = models.CharField(max_length=50, choices=GROUP_CHOICES, default='বিজ্ঞান')
    gpa = models.CharField(max_length=10, help_text="যেমন: ৪.৬৯")
    date_of_birth = models.DateField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.serial_no:
            self.serial_no = f"CC-{self.id:04d}"
            super().save(update_fields=['serial_no'])

    def __str__(self):
        return f"{self.student_name_bn} - {self.serial_no} ({self.status})"
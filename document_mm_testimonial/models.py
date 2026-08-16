from django.db import models

class StudentApplication(models.Model):
    BOARD_CHOICES = [
        ('মাধ্যমিক ও উচ্চ মাধ্যমিক শিক্ষা বোর্ড, রাজশাহী', 'মাধ্যমিক ও উচ্চ মাধ্যমিক শিক্ষা বোর্ড, রাজশাহী'),
        ('বাংলাদেশ কারিগরি শিক্ষা বোর্ড', 'বাংলাদেশ কারিগরি শিক্ষা বোর্ড'),
    ]

    DEPARTMENT_CHOICES = [
        ('মানবিক', 'মানবিক'),
        ('বিজ্ঞান', 'বিজ্ঞান'),
        ('এপারেল ম্যানুফেকচারিং বেসিকস', 'এপারেল ম্যানুফেকচারিং বেসিকস'),
        ('ফুড প্রসেসিং এন্ড প্রিজার্ভেশন', 'ফুড প্রসেসিং এন্ড প্রিজার্ভেশন'),
    ]

    GRADE_CHOICES = [
        ('A+', 'A+'),
        ('A', 'A'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B', 'B'),
        ('C', 'C'),
        ('D', 'D'),
    ]


    EXAM_MONTH_CHOICES = [
        ('জানুয়ারি', 'জানুয়ারি'),
        ('ফেব্রুয়ারি', 'ফেব্রুয়ারি'),
        ('মার্চ', 'মার্চ'),
        ('এপ্রিল', 'এপ্রিল'),
        ('মে', 'মে'),
        ('জুন', 'জুন'),
        ('জুলাই', 'জুলাই'),
        ('আগস্ট', 'আগস্ট'),
        ('সেপ্টেম্বর', 'সেপ্টেম্বর'),
        ('অক্টোবর', 'অক্টোবর'),
        ('নভেম্বর', 'নভেম্বর'),
        ('ডিসেম্বর', 'ডিসেম্বর'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    student_name_bn = models.CharField(max_length=255)
    date_of_birth = models.CharField(max_length=50)
    father_name_bn = models.CharField(max_length=255)
    mother_name_bn = models.CharField(max_length=255)
    village = models.CharField(max_length=255)
    post_office = models.CharField(max_length=100)
    upazila = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    passing_year = models.CharField(max_length=10)
    academic_year = models.CharField(max_length=50, default='2018-2019')
    exam_month = models.CharField(max_length=50, choices=EXAM_MONTH_CHOICES)
    board = models.CharField(max_length=100, choices=BOARD_CHOICES)
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES)
    GPA = models.CharField(max_length=10,)
    grade = models.CharField(max_length=10, choices=GRADE_CHOICES, default='A+')
    roll = models.CharField(max_length=50)
    registration_no = models.CharField(max_length=50)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student_name_bn} - {self.roll} ({self.status})"
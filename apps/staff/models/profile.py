from django.db import models
from django.conf import settings

class StaffProfile(models.Model):
    ROLE_CHOICES = [
        ('teacher', 'Teacher'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('on_leave', 'On Leave'),
    ]
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='staff_profile')
    employee_id = models.CharField(max_length=50, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='staff')
    designation = models.CharField(max_length=100)
    department = models.CharField(max_length=100, blank=True) # Could be a FK to Department model
    
    # Personal Info
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=20)
    date_of_birth = models.DateField(null=True, blank=True)
    blood_group = models.CharField(max_length=5, blank=True)
    marital_status = models.CharField(max_length=20, blank=True)
    joining_date = models.DateField()
    
    # Career Details
    qualification = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    previous_school = models.CharField(max_length=255, blank=True)
    
    # Contact
    address = models.TextField()
    permanent_address = models.TextField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Documents
    resume = models.FileField(upload_to='staff/resumes/', null=True, blank=True)
    joining_letter = models.FileField(upload_to='staff/joining_letters/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"

class StaffPayroll(models.Model):
    staff = models.OneToOneField(StaffProfile, on_delete=models.CASCADE, related_name='payroll')
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    contract_type = models.CharField(max_length=50) # e.g., Permanent, Contract
    work_shift = models.CharField(max_length=50) # e.g., Morning, Day
    
    # Bank Details
    bank_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=50)
    ifsc_code = models.CharField(max_length=20)
    branch_name = models.CharField(max_length=100)

    def __str__(self):
        return f"Payroll for {self.staff.employee_id}"

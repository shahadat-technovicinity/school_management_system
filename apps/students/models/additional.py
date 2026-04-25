from django.db import models
from django.core.validators import FileExtensionValidator
from .core import Student

class AdditionalDetails(models.Model):
    student = models.OneToOneField(
        Student, 
        on_delete=models.CASCADE, 
        related_name='additional_info',
        db_column='student_id'
    )

    # Transport Information
    route = models.CharField(max_length=100, blank=True, null=True)
    vehicle_number = models.CharField(max_length=50, blank=True, null=True)
    pickup_point = models.CharField(max_length=100, blank=True, null=True)

    # Hostel Information
    hostel_name = models.CharField(max_length=100, blank=True, null=True)
    room_no = models.CharField(max_length=50, blank=True, null=True)

    # Documents
    medical_certificate = models.FileField(
        upload_to='documents/medical/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        blank=True, null=True
    )
    transfer_certificate = models.FileField(
        upload_to='documents/transfer/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'])],
        blank=True, null=True
    )

    # Medical History
    MEDICAL_CONDITION_CHOICES = [
        ('Good', 'Good'),
        ('Bad', 'Bad'),
        ('Other', 'Other'),
    ]
    medical_condition = models.CharField(max_length=10, choices=MEDICAL_CONDITION_CHOICES, blank=True, null=True)
    Disease = models.CharField(max_length=100, blank=True, null=True)
    medication = models.CharField(max_length=100, blank=True, null=True)

    # Previous School Details
    previous_school_name = models.CharField(max_length=150, blank=True, null=True)
    previous_school_address = models.TextField(blank=True, null=True)

    # Other Details
    bank_name = models.CharField(max_length=100, blank=True, null=True)
    branch = models.CharField(max_length=100, blank=True, null=True)
    ifsc_number = models.CharField(max_length=20, blank=True, null=True)
    other_information = models.TextField(blank=True, null=True)

    # Admission Reference
    admission_reference = models.CharField(max_length=100, blank=True, null=True)

    # Sports
    sports = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = "student_profile_studentadditionalinfo"

    def __str__(self):
        return f"Extra Info of {self.student.full_name}"
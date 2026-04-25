from django.db import models
from django.core.validators import FileExtensionValidator
from .core import Student

class GuardianDetails(models.Model):
    student = models.OneToOneField(
        Student, 
        on_delete=models.CASCADE, 
        related_name='guardian_info',
        db_column='student_id'
    )

    GUARDIAN_TYPE_CHOICES = [
        ('Parent', 'Parent'),
        ('Guardian', 'Guardian'),
        ('Other', 'Other'),
    ]

    # Father's Info
    father_photo = models.ImageField(upload_to='student_profile_pictures/',
        blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        verbose_name="Profile Picture (300x300)")
    father_name = models.CharField(max_length=100)
    father_email = models.EmailField(blank=True, null=True)
    father_phone = models.CharField(max_length=20, blank=True, null=True)
    father_occupation = models.CharField(max_length=100, blank=True, null=True)
    father_nid_or_birth_certificate = models.CharField(max_length=50, blank=True, null=True)

    # Mother's Info
    mother_photo = models.ImageField(upload_to='student_profile_pictures/',
        blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        verbose_name="Profile Picture (300x300)")
    mother_name = models.CharField(max_length=100)
    mother_email = models.EmailField(blank=True, null=True)
    mother_phone = models.CharField(max_length=20, blank=True, null=True)
    mother_occupation = models.CharField(max_length=100, blank=True, null=True)
    mother_nid_or_birth_certificate = models.CharField(max_length=50, blank=True, null=True)

    # Guardian Details
    guardian_type = models.CharField(max_length=20, choices=GUARDIAN_TYPE_CHOICES, default='Parent')
    guardian_photo = models.ImageField(upload_to='student_profile_pictures/',
        blank=True, null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        verbose_name="Profile Picture (300x300)")
    guardian_name = models.CharField(max_length=100, blank=True, null=True)
    guardian_relation = models.CharField(max_length=50, blank=True, null=True)
    guardian_phone = models.CharField(max_length=20, blank=True, null=True)
    guardian_email = models.EmailField(blank=True, null=True)
    guardian_occupation = models.CharField(max_length=100, blank=True, null=True)
    guardian_address = models.TextField(blank=True, null=True)

    # Siblings
    sibling_studying_same_school = models.BooleanField(default=False)
    sibling_name = models.CharField(max_length=100, blank=True, null=True)
    sibling_admission_no = models.CharField(max_length=50, blank=True, null=True)

    # Address
    current_address = models.TextField(blank=True, null=True)
    permanent_address = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "student_profile_studentgurdianinfo"

    def __str__(self):
        return f"Guardian Info of {self.student.full_name}"

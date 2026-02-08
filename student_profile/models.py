# models.py
from django.db import models
from django.core.validators import RegexValidator, EmailValidator
from django.utils import timezone
from django.core.validators import FileExtensionValidator


def student_photo_upload_path(instance, filename):
    # upload to MEDIA_ROOT/students/<academic_year>/<admission_number>_<filename>
    year = (instance.academic_year or '').replace('/', '_')
    adm = instance.admission_number or 'unknown'
    return f"students/{year}/{adm}_{filename}"


class StudentPersonalInfo(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("alumni", "Alumni"),
        ("suspended", "Suspended"),
    ]

    SECTION_CHOICES = [
        ("section A", "Section A"),
        ("section B", "Section B"),
        ("section C", "Section C"),
        ("section D", "Section D"),

    ]
    
    CLASS_NAME_CHOICES = [
        ("class 6", "Class 6"),
        ("class 7", "Class 7"),
        ("class 8", "Class 8"),
        ("class 9", "Class 9"),
        ("class 10", "Class 10"),

    ]



    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]

    BLOOD_GROUP_CHOICES = [
        ("A+", "A+"), ("A-", "A-"),
        ("B+", "B+"), ("B-", "B-"),
        ("O+", "O+"), ("O-", "O-"),
        ("AB+", "AB+"), ("AB-", "AB-"),
    ]

    RELIGION_CHOICES = [
        ("islam", "Islam"),
        ("hindu", "Hindu"),
        ("christian", "Christian"),
        ("buddhism", "Buddhism"),
        ("others", "Others"),
    ]

    CATEGORY_CHOICES = [
        ("general", "General"),
        ("vocational", "Vocational"),

    ]

    SCHOLARSHIP_CHOICES = [
        ('hsp', 'HSP'),
        ('dte', 'DTE'),
        ('general scholarship', 'Genral Scholarship'),
        ('talentpul scholarship', 'Talentpul Scholarship'),
        ('hf', 'HF'),
        ('f', 'F'),
    ]

    academic_year = models.CharField(max_length=32)
    admission_number = models.CharField(max_length=64)
    admission_date = models.DateField()
    roll_number = models.CharField(max_length=32, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128, blank=True, null=True)

    class_name = models.CharField(max_length=64, choices=CLASS_NAME_CHOICES, blank=True, null=True)
    section = models.CharField(max_length=32, choices=SECTION_CHOICES,)

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()

    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES )
    house = models.CharField(max_length=64)
    religion = models.CharField(max_length=64, choices=RELIGION_CHOICES, blank=True, null=True)
    category = models.CharField(max_length=16, choices=CATEGORY_CHOICES, blank=True, null=True)

    primary_contact_number = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\+?\d{7,15}$', message="Enter a valid phone number with country code if applicable.")]
    )
    email_address = models.EmailField(blank=True, null=True, validators=[EmailValidator()])

    caste = models.CharField(max_length=128, blank=True, null=True)
    mother_tongue = models.CharField(max_length=64, blank=True, null=True)

    scholarship = models.CharField(max_length=25, choices=SCHOLARSHIP_CHOICES)

    photo = models.ImageField(upload_to='student_profile_pictures/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        help_text="Upload a profile photo (JPG or PNG, Max 1MB)",
        verbose_name="Profile Picture (300x300)")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Student Admission"
        verbose_name_plural = "Student Admissions"
        # academic_year + (admission_number or roll) should be unique together as a common constraint
        unique_together = (
            ('academic_year', 'admission_number'),
            # ('academic_year', 'roll_number'),  # uncomment if roll must be unique per year
        )
        indexes = [
            models.Index(fields=['academic_year', 'admission_number']),
            models.Index(fields=['class_name', 'section']),
        ]

    def __str__(self):
        if self.admission_number:
            return f"{self.first_name} {self.last_name or ''} ({self.admission_number})"
        return f"{self.first_name} {self.last_name or ''}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name or ''}".strip()

class StudentGurdianInfo(models.Model):
    student = models.OneToOneField(StudentPersonalInfo, on_delete=models.CASCADE, related_name='guardian_info')

    # Father's Info
    father_photo = models.ImageField(upload_to='student_profile_pictures/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        help_text="Upload a profile photo (JPG or PNG, Max 1MB)",
        verbose_name="Profile Picture (300x300)")
    father_name = models.CharField(max_length=100)
    father_email = models.EmailField(blank=True, null=True)
    father_phone = models.CharField(max_length=20, blank=True, null=True)
    father_occupation = models.CharField(max_length=100, blank=True, null=True)
    father_nid_or_birth_certificate = models.CharField(max_length=50, blank=True, null=True)

    # Mother's Info
    mother_photo = models.ImageField(upload_to='student_profile_pictures/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        help_text="Upload a profile photo (JPG or PNG, Max 1MB)",
        verbose_name="Profile Picture (300x300)")
    mother_name = models.CharField(max_length=100)
    mother_email = models.EmailField(blank=True, null=True)
    mother_phone = models.CharField(max_length=20, blank=True, null=True)
    mother_occupation = models.CharField(max_length=100, blank=True, null=True)
    mother_nid_or_birth_certificate = models.CharField(max_length=50, blank=True, null=True)

    # Guardian Details
    GUARDIAN_TYPE_CHOICES = [
        ('Parent', 'Parent'),
        ('Guardian', 'Guardian'),
        ('Other', 'Other'),
    ]
    guardian_type = models.CharField(max_length=20, choices=GUARDIAN_TYPE_CHOICES, default='Parent')
    guardian_photo = models.ImageField(upload_to='student_profile_pictures/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        help_text="Upload a profile photo (JPG or PNG, Max 1MB)",
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

    def __str__(self):
        return f"Guardian Info of {self.student.first_name} {self.student.last_name or ''}"

class StudentAdditionalInfo(models.Model):
    student = models.OneToOneField(StudentPersonalInfo, on_delete=models.CASCADE, related_name='additional_info')

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
    Disease  = models.CharField(max_length=100, blank=True, null=True)
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

    def __str__(self):
        return f"Extra Info of {self.student.first_name} {self.student.last_name or ''}"




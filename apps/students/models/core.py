from django.db import models
from django.core.validators import RegexValidator, EmailValidator, FileExtensionValidator
from apps.academics.models import AcademicYear, Class, Section
from academic_mm_class_and_section.models import AcademicClass, Section



def student_photo_upload_path(instance, filename):
    year = (instance.academic_year or '').replace('/', '_')
    adm = instance.admission_number or 'unknown'
    return f"students/{year}/{adm}_{filename}"


class Student(models.Model):
    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("alumni", "Alumni"),
        ("suspended", "Suspended"),
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
        ('general scholarship', 'General Scholarship'),
        ('talentpul scholarship', 'Talentpul Scholarship'),
        ('hf', 'HF'),
        ('f', 'F'),
    ]

    # Core Identifiers
    academic_year = models.CharField(max_length=32)
    admission_number = models.CharField(max_length=64)
    admission_date = models.DateField()
    roll_number = models.CharField(max_length=32, blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    # Name Fields
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128, blank=True, null=True)
    
    # 🟢 নতুন যোগ করা ফিল্ড ১: শিক্ষার্থীর নাম (বাংলা)
    full_name_bn = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name="Full Name (Bangla)"
    )

    # Replaced Static Text with ForeignKeys representing relational data
    class_name_static = models.ForeignKey(AcademicClass, on_delete=models.SET_NULL, null=True, blank=True)
    section_static = models.ForeignKey(Section, on_delete=models.SET_NULL, null=True, blank=True)

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    date_of_birth = models.DateField()

    # 🟢 নতুন যোগ করা ফিল্ড ২: শিক্ষার্থীর জন্মনিবন্ধন নম্বর (১৭ ডিজিট ভ্যালিডেশন সহ)
    birth_certificate_number = models.CharField(
        max_length=50, 
        blank=True, 
        null=True,
        validators=[RegexValidator(r'^\d{17}$', message="Enter a valid 17-digit birth certificate number.")],
        verbose_name="Birth Certificate Number"
    )

    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES)
    house = models.CharField(max_length=64, blank=True, null=True)
    religion = models.CharField(max_length=64, choices=RELIGION_CHOICES, blank=True, null=True)
    category = models.CharField(max_length=16, choices=CATEGORY_CHOICES, blank=True, null=True)

    primary_contact_number = models.CharField(
        max_length=20,
        validators=[RegexValidator(r'^\+?\d{7,15}$', message="Enter a valid phone number with country code if applicable.")]
    )
    email_address = models.EmailField(blank=True, null=True, validators=[EmailValidator()])

    caste = models.CharField(max_length=128, blank=True, null=True)
    mother_tongue = models.CharField(max_length=64, blank=True, null=True)

    scholarship = models.CharField(max_length=25, choices=SCHOLARSHIP_CHOICES, blank=True, null=True)

    # Identifiers & Security (Matching UI QR/Code features)
    student_id_card_code = models.CharField(max_length=100, unique=True, null=True, blank=True)
    qr_code_data = models.TextField(null=True, blank=True) 
    is_id_card_generated = models.BooleanField(default=False)

    photo = models.ImageField(
        upload_to=student_photo_upload_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        help_text="Upload a profile photo (JPG or PNG, Max 1MB)",
        verbose_name="Profile Picture (300x300)"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Student"
        verbose_name_plural = "Students"
        db_table = "student_profile_studentpersonalinfo"
        unique_together = (
            ('academic_year', 'admission_number'),
        )

    def __str__(self):
        if self.admission_number:
            return f"{self.first_name} {self.last_name or ''} ({self.admission_number})"
        return f"{self.first_name} {self.last_name or ''}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name or ''}".strip()
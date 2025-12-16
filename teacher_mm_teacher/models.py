from django.db import models
from django.conf import settings


class Teacher(models.Model):
    """
    Teacher profile model linked to User via OneToOne relationship.
    User model handles name, email, and password.
    """

    GENDER_CHOICES = [
        ("male", "Male"),
        ("female", "Female"),
        ("other", "Other"),
    ]

    BLOOD_GROUP_CHOICES = [
        ("A+", "A+"), ("A-", "A-"),
        ("B+", "B+"), ("B-", "B-"),
        ("AB+", "AB+"), ("AB-", "AB-"),
        ("O+", "O+"), ("O-", "O-"),
    ]

    MARITAL_STATUS_CHOICES = [
        ("single", "Single"),
        ("married", "Married"),
        ("divorced", "Divorced"),
        ("widowed", "Widowed"),
    ]

    STATUS_CHOICES = [
        ("active", "Active"),
        ("inactive", "Inactive"),
        ("on_leave", "On Leave"),
    ]

    CONTRACT_TYPE_CHOICES = [
        ("permanent", "Permanent"),
        ("contract", "Contract"),
        ("temporary", "Temporary"),
        ("part_time", "Part Time"),
    ]

    WORK_SHIFT_CHOICES = [
        ("morning", "Morning"),
        ("afternoon", "Afternoon"),
        ("evening", "Evening"),
        ("full_day", "Full Day"),
    ]

    # ─────────────────────────────────────────────────────────────
    # User Relationship (OneToOne)
    # ─────────────────────────────────────────────────────────────
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teacher_profile",
        help_text="Linked user account for authentication",
        null=True,  # Allow null temporarily for migration, should be non-null in production
        blank=True
    )

    # ─────────────────────────────────────────────────────────────
    # Personal Information
    # ─────────────────────────────────────────────────────────────
    teacher_id = models.CharField(max_length=50, unique=True, help_text="Unique teacher identifier")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, blank=True)
    languages_known = models.JSONField(default=list, blank=True, help_text="List of languages known")
    class_assigned = models.CharField(max_length=100, blank=True)
    subject = models.CharField(max_length=100, blank=True)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True)
    primary_contact_number = models.CharField(max_length=20, blank=True)
    father_name = models.CharField(max_length=150, blank=True)
    mother_name = models.CharField(max_length=150, blank=True)
    qualification = models.CharField(max_length=255, blank=True)
    work_experience = models.CharField(max_length=255, blank=True)

    # Previous Employment
    previous_school_name = models.CharField(max_length=255, blank=True)
    previous_school_address = models.CharField(max_length=255, blank=True)
    previous_school_phone = models.CharField(max_length=25, blank=True)

    # Address
    permanent_address = models.TextField(blank=True)
    current_address = models.TextField(blank=True)

    # Identification
    pan_number = models.CharField(max_length=50, blank=True, help_text="PAN or Tax ID number")

    # ─────────────────────────────────────────────────────────────
    # Payroll Information
    # ─────────────────────────────────────────────────────────────
    epf_no = models.CharField(max_length=50, blank=True, help_text="Employee Provident Fund number")
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    contract_type = models.CharField(max_length=50, choices=CONTRACT_TYPE_CHOICES, blank=True)
    work_shift = models.CharField(max_length=50, choices=WORK_SHIFT_CHOICES, blank=True)
    work_location = models.CharField(max_length=100, blank=True)
    date_of_joining = models.DateField(null=True, blank=True)
    date_of_leaving = models.DateField(null=True, blank=True)

    # ─────────────────────────────────────────────────────────────
    # Leave Allocation
    # ─────────────────────────────────────────────────────────────
    medical_leaves = models.PositiveIntegerField(default=0)
    casual_leaves = models.PositiveIntegerField(default=0)
    maternity_leaves = models.PositiveIntegerField(default=0)
    sick_leaves = models.PositiveIntegerField(default=0)

    # ─────────────────────────────────────────────────────────────
    # Bank Details
    # ─────────────────────────────────────────────────────────────
    account_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    bank_name = models.CharField(max_length=100, blank=True)
    branch_name = models.CharField(max_length=100, blank=True)
    ifsc_code = models.CharField(max_length=50, blank=True)

    # ─────────────────────────────────────────────────────────────
    # Transport Details
    # ─────────────────────────────────────────────────────────────
    route_id = models.CharField(max_length=50, blank=True)
    vehicle_number = models.CharField(max_length=50, blank=True)
    pickup_point = models.CharField(max_length=100, blank=True)

    # ─────────────────────────────────────────────────────────────
    # Hostel Details
    # ─────────────────────────────────────────────────────────────
    hostel_id = models.CharField(max_length=50, blank=True)
    room_no = models.CharField(max_length=50, blank=True)

    # ─────────────────────────────────────────────────────────────
    # Social Media Links
    # ─────────────────────────────────────────────────────────────
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    youtube = models.URLField(blank=True)
    twitter = models.URLField(blank=True)

    # ─────────────────────────────────────────────────────────────
    # Documents (File Uploads)
    # ─────────────────────────────────────────────────────────────
    photo = models.ImageField(upload_to="teachers/photos/", null=True, blank=True)
    resume = models.FileField(upload_to="teachers/resume/", null=True, blank=True)
    joining_letter = models.FileField(upload_to="teachers/joining_letter/", null=True, blank=True)

    # ─────────────────────────────────────────────────────────────
    # Additional Info
    # ─────────────────────────────────────────────────────────────
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    notes = models.TextField(blank=True)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Teacher"
        verbose_name_plural = "Teachers"

    def __str__(self) -> str:
        if self.user:
            return f"{self.teacher_id} - {self.user.name}"
        return f"{self.teacher_id}"

    @property
    def full_name(self) -> str:
        """Return the user's full name."""
        if self.user:
            return self.user.name
        return ""

    @property
    def email(self) -> str:
        """Return the user's email (username in this case)."""
        if self.user:
            return self.user.username
        return ""

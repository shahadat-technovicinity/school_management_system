from django.db import models
from django.conf import settings
from academic_mm_class_and_section.models import AcademicClass, Section


# ─────────────────────────────────────────────────────────────
# Single Teacher & Staff Profile Model
# ─────────────────────────────────────────────────────────────

class TeacherAndStaffProfile(models.Model):
    """
    Unified profile model for Teachers and Staff members,
    linked to User via OneToOne relationship.
    """

    # Category Selection (Teacher vs Staff)
    EMPLOYEE_TYPE_CHOICES = [
        ("teacher", "Teacher"),
        ("staff", "Staff"),
    ]

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
    # User Connection & Category Type
    # ─────────────────────────────────────────────────────────────

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="teacher_staff_profile",
        help_text="Linked user account created during Auth",
        null=True,
        blank=True
    )

    # Main flag to separate Teacher from Staff
    employee_type = models.CharField(
        max_length=20,
        choices=EMPLOYEE_TYPE_CHOICES,
        default="teacher",
        help_text="Select whether this profile belongs to a Teacher or Staff"
    )

    designation = models.CharField(
        max_length=150, 
        blank=True, 
        help_text="Designation e.g. Senior Math Teacher, Accountant, Office Assistant"
    )

    department = models.CharField(
        max_length=150, 
        blank=True, 
        help_text="Department e.g. Science, Accounts, Administration"
    )


    # ─────────────────────────────────────────────────────────────
    # Personal Information
    # ─────────────────────────────────────────────────────────────

    name_bn = models.CharField(max_length=255, blank=True, help_text="বাংলা নাম")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    marital_status = models.CharField(max_length=20, choices=MARITAL_STATUS_CHOICES, blank=True)
    languages_known = models.JSONField(default=list, blank=True, help_text="List of languages known")

    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUP_CHOICES, blank=True)
    primary_contact_number = models.CharField(max_length=20, blank=True)
    
    father_name = models.CharField(max_length=150, blank=True)
    father_name_bn = models.CharField(max_length=150, blank=True, help_text="বাবার বাংলা নাম")
    mother_name = models.CharField(max_length=150, blank=True)
    mother_name_bn = models.CharField(max_length=150, blank=True, help_text="মায়ের বাংলা নাম")
    
    qualification = models.CharField(max_length=255, blank=True)
    work_experience = models.CharField(max_length=255, blank=True)

    # Previous Employment
    previous_school_name = models.CharField(max_length=255, blank=True)
    previous_school_address = models.CharField(max_length=255, blank=True)
    previous_school_phone = models.CharField(max_length=25, blank=True)

    # Address & Location
    district = models.CharField(max_length=100, blank=True, help_text="নিজ জেলা")
    permanent_address = models.TextField(blank=True)
    current_address = models.TextField(blank=True)

    # Identification
    nid_number = models.CharField(max_length=50, blank=True, help_text="NID নম্বর")
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

    route_id = models.CharField(max_length=50, blank=True, null=True)
    vehicle_number = models.CharField(max_length=50, blank=True, null=True)
    pickup_point = models.CharField(max_length=100, blank=True, null=True)


    # ─────────────────────────────────────────────────────────────
    # Hostel Details
    # ─────────────────────────────────────────────────────────────

    hostel_id = models.CharField(max_length=50, blank=True)
    room_no = models.CharField(max_length=50, blank=True)


    # ─────────────────────────────────────────────────────────────
    # Social Media Links
    # ─────────────────────────────────────────────────────────────

    facebook = models.CharField(max_length=200, blank=True, null=True)
    instagram = models.CharField(max_length=200, blank=True, null=True)
    linkedin = models.CharField(max_length=200, blank=True, null=True)
    youtube = models.CharField(max_length=200, blank=True, null=True)
    twitter = models.CharField(max_length=200, blank=True, null=True)


    # ─────────────────────────────────────────────────────────────
    # Documents (File Uploads)
    # ─────────────────────────────────────────────────────────────

    photo = models.ImageField(upload_to="teacher_staff/photos/", null=True, blank=True)
    resume = models.FileField(upload_to="teacher_staff/resumes/", null=True, blank=True)
    joining_letter = models.FileField(upload_to="teacher_staff/joining_letters/", null=True, blank=True)
    office_order_copy = models.FileField(upload_to="teacher_staff/office_orders/", null=True, blank=True)
    nid_card_copy = models.FileField(upload_to="teacher_staff/nid_cards/", null=True, blank=True)


    # ─────────────────────────────────────────────────────────────
    # Status & Timestamps
    # ─────────────────────────────────────────────────────────────

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Teacher & Staff Profile"
        verbose_name_plural = "Teacher & Staff Profiles"


    def __str__(self) -> str:
        if self.user:
            name = self.user.get_full_name() or self.user.username
            return f"{name} ({self.get_employee_type_display()})"
        return f"Profile ID {self.id} ({self.get_employee_type_display()})"


    @property
    def full_name(self) -> str:
        """Returns full name from linked User account."""
        if self.user:
            return self.user.get_full_name() or self.user.username
        return ""


    @property
    def email(self) -> str:
        """Returns email or username from linked User account."""
        if self.user:
            return self.user.email or self.user.username
        return ""
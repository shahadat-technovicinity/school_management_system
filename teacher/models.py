from django.db import models


class Teacher(models.Model):
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

    teacher_id = models.CharField(max_length=50, unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, blank=True)

    class_assigned = models.CharField(max_length=100, blank=True)
    subject = models.CharField(max_length=100, blank=True)

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    primary_contact_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    date_of_joining = models.DateField(null=True, blank=True)

    father_name = models.CharField(max_length=150, blank=True)
    mother_name = models.CharField(max_length=150, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    marital_status = models.CharField(max_length=10, choices=MARITAL_STATUS_CHOICES, blank=True)

    # Store multiple languages; JSONField is simple and portable.
    languages_known = models.JSONField(default=list, blank=True)

    qualification = models.CharField(max_length=255, blank=True)
    work_experience = models.CharField(max_length=255, blank=True)

    previous_school_name = models.CharField(max_length=255, blank=True)
    previous_school_address = models.CharField(max_length=255, blank=True)
    previous_school_phone = models.CharField(max_length=20, blank=True)

    address = models.CharField(max_length=255, blank=True)
    permanent_address = models.CharField(max_length=255, blank=True)

    pan_or_id_number = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")

    notes = models.TextField(blank=True)

    photo = models.ImageField(upload_to="teacher_photos/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.teacher_id} - {self.first_name} {self.last_name}".strip()

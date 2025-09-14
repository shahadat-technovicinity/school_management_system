# admissions/models.py

from django.db import models
from django.core.validators import FileExtensionValidator

class StudentAdmission(models.Model):
    desired_class_CHOICES = [
        ('class 6', 'class 6'),
        ('class 9', 'class 9'),
        ('other', 'Other'),
    ]

    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    ]

    RELIGION_CHOICES = [
        ('islam', 'Islam'),
        ('hindu', 'Hindu'),
        ('buddhist', 'Buddhist'),
        ('christian', 'Christian'),
        ('other', 'Other'),
        ('not_specified', 'Not Specified'),
    ]

    desired_class = models.CharField(max_length=100, choices=desired_class_CHOICES, verbose_name="Desired Class for Admission")

    student_name_english = models.CharField(max_length=255, verbose_name="Student's Name (English)")
    student_name_bangla = models.CharField(max_length=255, verbose_name="Student's Name (Bangla)", blank=True, null=True)

    birth_registration_number = models.CharField(max_length=100, unique=True, verbose_name="Birth Registration Number")
    date_of_birth = models.DateField(verbose_name="Date of Birth")

    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name="Gender")
    religion = models.CharField(max_length=50, choices=RELIGION_CHOICES, verbose_name="Religion")

    profile_picture = models.ImageField(
        upload_to='student_profile_pictures/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])],
        help_text="Upload a profile photo (JPG or PNG, Max 1MB)",
        verbose_name="Profile Picture (300x300)"
    )

    admission_date = models.DateField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    # status = models.CharField(max_length=50, default='pending', verbose_name="Admission Status")

    class Meta:
        verbose_name = "Student Admission Form"
        verbose_name_plural = "Student Admission Forms"
        ordering = ['-admission_date']


########## Gurdian information ################################
########## Gurdian information ################################
########## Gurdian information ################################
########## Gurdian information ################################
    # Father's Information
    father_name_en = models.CharField(max_length=255, null=True, blank=True)
    father_name_bn = models.CharField(max_length=255, null=True, blank=True)
    father_nid_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    father_is_deceased = models.BooleanField(default=False)

    # Mother's Information
    mother_name_en = models.CharField(max_length=255, null=True, blank=True)
    mother_name_bn = models.CharField(max_length=255, null=True, blank=True)
    mother_nid_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    mother_is_deceased = models.BooleanField(default=False)
    
   

#########  Contact info................... ############################
#########  Contact info................... ############################
#########  Contact info................... ############################
#########  Contact info................... ############################
#########  Contact info................... ############################
    # Contact Information
    mobile_number = models.CharField(max_length=20)
    whatsapp_available = models.BooleanField(default=False)
    guardian_profession = models.CharField(max_length=255, null=True, blank=True)
    family_annual_income = models.CharField(max_length=100, null=True, blank=True)
    
    # Present Address
    present_address_village = models.CharField(max_length=255, null=True, blank=True)
    present_address_post_office = models.CharField(max_length=255, null=True, blank=True)
    present_address_sub_district = models.CharField(max_length=255, null=True, blank=True)
    present_address_district = models.CharField(max_length=255, null=True, blank=True)
    
    # Permanent Address
    is_permanent_same_as_present = models.BooleanField(default=False)
    permanent_address_village = models.CharField(max_length=255, null=True, blank=True)
    permanent_address_post_office = models.CharField(max_length=255, null=True, blank=True)
    permanent_address_sub_district = models.CharField(max_length=255, null=True, blank=True)
    permanent_address_district = models.CharField(max_length=255, null=True, blank=True)

    


###########   Academic Background..............   ################
###########   Academic Background..............   ################
###########   Academic Background..............   ################
###########   Academic Background..............   ################
###########   Academic Background..............   ################



    school_name = models.CharField(max_length=255)
    School_address = models.CharField(max_length=255)
    passing_class = models.CharField(max_length=50)
    roll = models.IntegerField()
    gpa = models.FloatField()
    passing_year = models.IntegerField()
    sibling_id_number = models.CharField(max_length=255, blank=True, null=True)

    


################   Special skills #####################

    # Special Skills using CharField with multiple choices
    SPECIAL_SKILLS_CHOICES = [
        ('Cricket', 'Cricket'),
        ('Football', 'Football'),
        ('Dance', 'Dance'),
        ('Singing', 'Singing'),
        ('Ham/Naat', 'Ham/Naat'),
        ('Qirat', 'Qirat'),
        ('Chess', 'Chess'),
        ('Badminton', 'Badminton'),
        ('Shot Put', 'Shot Put'),
        ('Swimming', 'Swimming'),
    ]

   
    special_skills = models.CharField(
        max_length=255,
        choices=SPECIAL_SKILLS_CHOICES,
        blank=True,
        null=True
    )

    additional_comments = models.TextField(blank=True, null=True)
    
    # Agreement checkbox
    agreed_to_terms = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.student_name_english} - Admission"

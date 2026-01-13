from django.db import models

# Create your models here.
# institution/models.py

from django.db import models

class Institution(models.Model):
    INSTITUTE_TYPE_CHOICES = [
        ('School', 'School'),
        ('College', 'College'),
        ('Madrasa', 'Madrasa'),
    ]
    
    DIVISION_CHOICES = [
        ('DHAKA', 'Dhaka'),
        ('CHITTAGONG', 'Chittagong'),
        ('RAJSHAHI', 'Rajshahi'),
        ('KHULNA', 'Khulna'),
        ('BARISAL', 'Barisal'),
        ('SYLHET', 'Sylhet'),
        ('RANGPUR', 'Rangpur'),
        ('MYMENSINGH', 'Mymensingh'),
    ]
    
    # Basic Information
    institute_name_local = models.CharField(max_length=255)
    eiin = models.CharField(max_length=10, unique=True)
    institute_type = models.CharField(max_length=50, choices=INSTITUTE_TYPE_CHOICES)
    education_board_code = models.CharField(max_length=10)
    school = models.CharField(max_length=10)
    emis_code = models.CharField(max_length=20)
    mpo_code = models.CharField(max_length=20, blank=True)
    technical_mpo_code = models.CharField(max_length=50, blank=True)
    
    # Location
    district = models.CharField(max_length=100)
    division = models.CharField(max_length=50, choices=DIVISION_CHOICES)
    parliamentary_constituency = models.CharField(max_length=100, blank=True)
    sub_district_thana = models.CharField(max_length=100)
    village_road_area = models.CharField(max_length=255)
    union = models.CharField(max_length=100, blank=True)
    mouza_mahalla_name = models.CharField(max_length=255, blank=True)
    mouza_mahalla_number = models.CharField(max_length=50, blank=True)
    post_office = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    
    # Contact Information
    institute_phone = models.CharField(max_length=20, blank=True)
    institute_mobile = models.CharField(max_length=20)
    institute_fax = models.CharField(max_length=20, blank=True)
    institute_email = models.EmailField()
    website_address = models.URLField(blank=True)
    
    # Head of Institution
    head_of_institute = models.CharField(max_length=255)
    head_mobile = models.CharField(max_length=20)
    institute_name_eng = models.CharField(max_length=100)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.institute_name_local
    


#### istitute details

# institution/models.py


class InstitutionDetails(models.Model):
    ACADEMIC_LEVEL_CHOICES = [
        ('Junior', 'Junior'),
        ('Secondary', 'Secondary'),
        ('Higher Secondary', 'Higher Secondary'),
    ]
    
    SUBJECT_CHOICES = [
        ('BANGLA', 'Bangla'),
        ('ENGLISH', 'English'),
    ]
    
    GROUP_CHOICES = [
        ('Science', 'Science'),
        ('Business Studies', 'Business Studies'),
        ('Commerce', 'Commerce'),
        ('Humanities', 'Humanities'),
    ]
    
    MEDIUM_CHOICES = [
        ('BN', 'Bangla'),
        ('EN', 'English'),
        ('UM', 'Urdu'),
    ]
    
    FOR_WHOM_CHOICES = [
        ('Boys', 'Boys'),
        ('Girls', 'Girls'),
        ('Co-Educational(Combined)', 'Co-Educational(Combined)'),
    ]
    
    SHIFT_CHOICES = [
        ('Day', 'Day'),
        ('Morning', 'Morning'),
        ('Evening', 'Evening'),
    ]
    
    RECOGNITION_CHOICES = [
        ('Recognized', 'Recognized (স্বীকৃত)'),
        ('Non-Govt', 'Non-Govt (বেসরকারী)'),
    ]
    
    # Institute Information
    institute = models.ForeignKey(
        Institution, 
        on_delete=models.CASCADE, 
        related_name='details'
    )
    date_of_establishment = models.DateField()
    subjects = models.JSONField(default=list)  # ['BANGLA', 'ENGLISH']
    academic_levels = models.JSONField(default=list)  # ['Junior', 'Secondary']
    groups = models.JSONField(default=list)  # ['Science', 'Business Studies']
    medium = models.CharField(max_length=10, choices=MEDIUM_CHOICES)
    for_whom = models.CharField(max_length=50, choices=FOR_WHOM_CHOICES)
    management_type = models.CharField(max_length=100, blank=True)
    shift = models.CharField(max_length=20, choices=SHIFT_CHOICES)
    recognition = models.CharField(max_length=50, choices=RECOGNITION_CHOICES)
    
    # Approval/Recognition Information
    approval_level = models.CharField(max_length=100, blank=True)
    max_permitted_level = models.CharField(max_length=100, blank=True)
    date_of_first_recognition = models.DateField(null=True, blank=True)
    expiry_date_of_recognition = models.DateField(null=True, blank=True)
    
    # MPO Information
    institution_mpo_enlistment = models.BooleanField(default=False)
    mpo_level = models.CharField(max_length=50, blank=True)
    date_of_mpo_enlistment = models.DateField(null=True, blank=True)
    mpo_code = models.CharField(max_length=50, blank=True)
    mpo_evidence_technical = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Institution Details - {self.date_of_establishment}"
    


#Institute info Bank Details
class InstituteInfoBank(models.Model):
    institute = models.ForeignKey(
        Institution, 
        on_delete=models.CASCADE, 
        related_name='banks'
    )
    bank_name = models.CharField(max_length=255, verbose_name="Bank")
    branch_name = models.CharField(max_length=255, verbose_name="Branch")
    routing_number = models.CharField(max_length=20, verbose_name="Routing Number")
    
    ACCOUNT_TYPE_CHOICES = [
        ('savings', 'Savings'),
        ('current', 'Current'),
    ]
    account_type = models.CharField(
        max_length=50, 
        choices=ACCOUNT_TYPE_CHOICES,
        verbose_name="Type of Account"
    )
    
    account_holder_name = models.CharField(max_length=255, verbose_name="Account Holder Name")
    account_number = models.CharField(max_length=50, verbose_name="Account Number")
    
    purpose_of_account = models.TextField(blank=True, null=True, verbose_name="Purpose of Account")

    def __str__(self):
        return f"{self.account_holder_name} - {self.bank_name}"
    



class InstituteOthers(models.Model):
    institute = models.ForeignKey(
        Institution, 
        on_delete=models.CASCADE, 
        related_name='others'
    )
    nationalization_date = models.DateField(null=True, blank=True)
    administrative_unit = models.CharField(max_length=100, null=True, blank=True)
    admin_unit_distance = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    location_type = models.CharField(max_length=50, null=True, blank=True)
    geographic_location_type = models.CharField(max_length=100, null=True, blank=True)
    is_in_enclave = models.CharField(max_length=10, default='No')
    any_case_in_institute = models.CharField(max_length=10, default='No')

    def __str__(self):
        return f"Details of {self.administrative_unit}"
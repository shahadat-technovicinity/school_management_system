from django.db import models

# Create your models here.
class stipend_student(models.Model):
    STIPEND_TYPE_CHOICHES = [
        ('Merit', 'Merit-Based'),
        ('Special', 'Special Categories'),
        ('Financial', 'Financial Aid'),
        ('Sports', 'Sports Scholarship'),
    ]
        
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Completed', 'Completed'),
    ]

    CLASS_NAME_CHOICES = [
        ('class 6', 'Class 6'),
        ('class 7', 'Class 7'),
        ('class 8', 'Class 8'),
        ('class 9', 'Class 9'),
        ('class 10', 'Class 10'),
    ]
    student_id = models.CharField(max_length=50)
    student_name = models.CharField(max_length=50)
    class_name = models.CharField(max_length=50, choices=CLASS_NAME_CHOICES)
    stipend_type = models.CharField(max_length=50, choices=STIPEND_TYPE_CHOICHES)
    amount = models.CharField(max_length=50)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()


    def __str__(self):
        return f"{self.student_name}"
    


class stipend_free_hf(models.Model):
    CONCESSION_TYPE_CHOICHES = [
        ('full free', 'Full Free'),
        ('half free', 'Half Free'),
        
    ]
        
    CATEGORY_CHOICES = [
        ('low income', 'Low Income'),
        ('meritorious', 'Meritorious'),
        ('special cases', 'Special Cases'),
        ('staff children', 'Staff Children'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Completed', 'Completed'),
    ]


    CLASS_NAME_CHOICES = [
        ('class 6', 'Class 6'),
        ('class 7', 'Class 7'),
        ('class 8', 'Class 8'),
        ('class 9', 'Class 9'),
        ('class 10', 'Class 10'),
    ]
    student_id = models.CharField(max_length=50)
    student_name = models.CharField(max_length=50)
    class_name = models.CharField(max_length=50, choices=CLASS_NAME_CHOICES)
    concession_type = models.CharField(max_length=50, choices=CONCESSION_TYPE_CHOICHES)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    valid_till = models.DateField()
    original_fee = models.CharField(max_length=100)
    concession_ammount = models.CharField(max_length=100)
    reason_for_concession = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES)


    def __str__(self):
        return f"{self.student_name}"
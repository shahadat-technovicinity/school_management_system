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
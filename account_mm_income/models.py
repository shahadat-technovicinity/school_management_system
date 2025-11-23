from django.db import models

# Create your models here.
class account_Income(models.Model):
    INCOME_CATEGORIES = [
        ('student salary', 'Student Salary'),
        ('session fees', 'Session Fees'),
        ('exam fees', 'Exam Fees'),                                        
        ('form filup', 'Form Filup'),
        ('shop rent', 'Shop Rent'),
        ('land rent', 'Land Rent'),
        ('donation', 'Donation'),
    ]
    income_category = models.CharField(max_length=50, choices=INCOME_CATEGORIES)
    
    amount = models.DecimalField(max_digits=12, decimal_places=2) 
    date = models.DateField()
    description = models.TextField(blank=True, null=True)
    voucher_file = models.FileField(upload_to='income_vouchers/', blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.amount}"
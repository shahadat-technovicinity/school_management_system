from django.db import models
from datetime import date

class ExpenseVoucher(models.Model):
    DEPOSITE_CATEGORY_CHOICES = [
        ('general', 'General'),
        ('exam', 'Exam'),
        ('govt. salary', 'Govt. Salary'),
        ('tuition fee', 'Tuition Fee'),
        ('science', 'Science'),
    ]    
    date = models.DateField()
    deposit_category = models.CharField(max_length=100, choices=DEPOSITE_CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # এখন আইডি (PK) ব্যবহার করা হবে
        return f"Voucher #{self.pk}" 

    class Meta:
        ordering = ['-created_at']
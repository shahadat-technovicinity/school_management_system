import datetime
from django.db import models

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('Facilities', 'Facilities & Maintenance'),
        ('Academic', 'Academic Resources'),
        ('Salary', 'Staff Salaries'),
        ('Transport', 'Transportation'),
        ('Tech', 'Technology'),
        ('Others', 'Others'),
    ]
    voucher_no = models.CharField(max_length=50, unique=True, editable=False)
    
    expense_category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    expense_date = models.DateField()
    description = models.TextField()
    voucher_file = models.FileField(upload_to='expenses/vouchers/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.voucher_no:
            date_str = datetime.datetime.now().strftime('%y%m%d')
            last_expense = Expense.objects.filter(voucher_no__contains=date_str).last()
            
            if last_expense:
                last_serial = int(last_expense.voucher_no[-2:])
                new_serial = str(last_serial + 1).zfill(2)
            else:
                new_serial = '01'
            
            self.voucher_no = f'EXP-{date_str}{new_serial}'
            
        super(Expense, self).save(*args, **kwargs)

    class Meta:
        ordering = ['-expense_date']
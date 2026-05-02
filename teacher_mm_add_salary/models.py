from django.db import models
from django.conf import settings


class SalaryRecord(models.Model):
    POSITION_CHOICES = [
        ('Science Teacher', 'Science Teacher'),
        ('Arts Teacher', 'Arts Teacher'),
        ('English Teacher', 'English Teacher'),
        ('Senior Staff', 'Senior Staff'),
        ('Junior Staff', 'Junior Staff'),
    ]
    DEPARTMENT_CHOICES = [
        ('Teaching', 'Teaching'),
        ('Administration', 'Administration'),
        ('Accounts', 'Accounts'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('Bank Transfer', 'Bank Transfer'),
        ('Cash', 'Cash'),
        ('Cheque', 'Cheque'),
        ('Mobile Banking', 'Mobile Banking'),
    ]
    FREQUENCY_CHOICES = [
        ('Monthly', 'Monthly'),
        ('Yearly', 'Yearly'),
        ('Weekly', 'Weekly'),
    ]
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
    ]

    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role__in': ['Teacher', 'Staff']}
    )
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES, default='Teaching')
    position = models.CharField(max_length=100, choices=POSITION_CHOICES)
    basic_salary = models.DecimalField(max_digits=12, decimal_places=2)
    payment_frequency = models.CharField(max_length=50, choices=FREQUENCY_CHOICES, default='Monthly')
    payment_method = models.CharField(max_length=100, choices=PAYMENT_METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    comments = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee} - {self.basic_salary}"


class Allowance(models.Model):
    salary_record = models.ForeignKey(SalaryRecord, related_name='allowances', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.amount}"


class Deduction(models.Model):
    salary_record = models.ForeignKey(SalaryRecord, related_name='deductions', on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.amount}"


class ExtraWork(models.Model):
    WORK_TYPE_CHOICES = [
        ('Extra Class', 'Extra Class'),
        ('Overtime', 'Overtime'),
    ]
    salary_record = models.ForeignKey(SalaryRecord, related_name='extra_works', on_delete=models.CASCADE)
    work_type = models.CharField(max_length=100, choices=WORK_TYPE_CHOICES)
    hours = models.DecimalField(max_digits=5, decimal_places=2)
    rate_per_hour = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.work_type} - {self.hours} hours"


class PaymentHistory(models.Model):
    salary_record = models.ForeignKey(SalaryRecord, related_name='payment_history', on_delete=models.CASCADE)
    month = models.CharField(max_length=20)
    year = models.IntegerField()
    net_salary = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, default='Paid')
    payment_date = models.DateField()

    def __str__(self):
        return f"{self.salary_record.employee.name} - {self.month} {self.year}"
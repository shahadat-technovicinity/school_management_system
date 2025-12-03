"""
Salary Management Models

This module contains models for managing employee salaries including:
- EmployeeSalary: Main salary record for each employee per month
- SalaryAllowance: Dynamic allowances (housing, transport, medical, custom)
- SalaryDeduction: Dynamic deductions (tax, pension, insurance, custom)
"""

from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from teacher.models import Teacher


class EmployeeSalary(models.Model):
    """
    Main salary record for an employee for a specific month.
    Links to Teacher model and contains all salary components.
    """

    class PaymentFrequency(models.TextChoices):
        MONTHLY = "monthly", "Monthly"
        WEEKLY = "weekly", "Weekly"
        BIWEEKLY = "biweekly", "Bi-Weekly"
        YEARLY = "yearly", "Yearly"

    class PaymentMethod(models.TextChoices):
        DIRECT_DEPOSIT = "direct_deposit", "Direct Deposit"
        BANK_TRANSFER = "bank_transfer", "Bank Transfer"
        CASH = "cash", "Cash"
        CHECK = "check", "Check"

    class PaymentStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"
        PROCESSING = "processing", "Processing"
        CANCELLED = "cancelled", "Cancelled"

    # Employee relationship
    employee = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="salaries",
        help_text="The employee/teacher this salary belongs to"
    )

    # Salary period (stored as first day of month for easy querying)
    month = models.DateField(
        help_text="Salary month (stored as first day of month, e.g., 2025-05-01)"
    )

    # Salary components
    basic_salary = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Base salary amount"
    )

    payment_frequency = models.CharField(
        max_length=20,
        choices=PaymentFrequency.choices,
        default=PaymentFrequency.MONTHLY,
        help_text="How often salary is paid"
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.BANK_TRANSFER,
        help_text="Method of payment"
    )

    # Payment status
    payment_status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        help_text="Current payment status"
    )

    payment_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date and time when payment was made"
    )

    # Additional info
    comments = models.TextField(
        blank=True,
        default="",
        help_text="Additional notes or comments about this salary"
    )

    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        "userauthentication.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_salaries",
        help_text="User who created this record"
    )
    paid_by = models.ForeignKey(
        "userauthentication.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="paid_salaries",
        help_text="User who processed the payment"
    )

    class Meta:
        db_table = "employee_salary"
        verbose_name = "Employee Salary"
        verbose_name_plural = "Employee Salaries"
        ordering = ["-month", "employee__user__name"]
        # Ensure one salary record per employee per month
        unique_together = ["employee", "month"]
        indexes = [
            models.Index(fields=["month"]),
            models.Index(fields=["payment_status"]),
            models.Index(fields=["employee", "month"]),
        ]

    def __str__(self):
        return f"{self.employee.user.name} - {self.month.strftime('%B %Y')}"

    @property
    def total_allowances(self) -> Decimal:
        """Calculate total allowances from related SalaryAllowance records."""
        return self.allowances.aggregate(
            total=models.Sum("amount")
        )["total"] or Decimal("0.00")

    @property
    def total_deductions(self) -> Decimal:
        """Calculate total deductions from related SalaryDeduction records."""
        return self.deductions.aggregate(
            total=models.Sum("amount")
        )["total"] or Decimal("0.00")

    @property
    def net_salary(self) -> Decimal:
        """Calculate net salary: basic + allowances - deductions."""
        return self.basic_salary + self.total_allowances - self.total_deductions

    @property
    def gross_salary(self) -> Decimal:
        """Calculate gross salary: basic + allowances."""
        return self.basic_salary + self.total_allowances


class SalaryAllowance(models.Model):
    """
    Dynamic allowance entries for a salary record.
    Examples: Housing, Transport, Medical, Meal, etc.
    """

    class AllowanceType(models.TextChoices):
        HOUSING = "housing", "Housing Allowance"
        TRANSPORT = "transport", "Transport Allowance"
        MEDICAL = "medical", "Medical Allowance"
        MEAL = "meal", "Meal Allowance"
        PHONE = "phone", "Phone Allowance"
        EDUCATION = "education", "Education Allowance"
        OVERTIME = "overtime", "Overtime Pay"
        BONUS = "bonus", "Bonus"
        OTHER = "other", "Other"

    salary = models.ForeignKey(
        EmployeeSalary,
        on_delete=models.CASCADE,
        related_name="allowances",
        help_text="The salary record this allowance belongs to"
    )

    allowance_type = models.CharField(
        max_length=20,
        choices=AllowanceType.choices,
        default=AllowanceType.OTHER,
        help_text="Type of allowance"
    )

    name = models.CharField(
        max_length=100,
        help_text="Name/description of the allowance"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Allowance amount"
    )

    class Meta:
        db_table = "salary_allowance"
        verbose_name = "Salary Allowance"
        verbose_name_plural = "Salary Allowances"
        ordering = ["allowance_type", "name"]

    def __str__(self):
        return f"{self.name}: {self.amount}"


class SalaryDeduction(models.Model):
    """
    Dynamic deduction entries for a salary record.
    Examples: Tax, Pension, Health Insurance, Loan, etc.
    """

    class DeductionType(models.TextChoices):
        INCOME_TAX = "income_tax", "Income Tax"
        PENSION = "pension", "Pension Fund"
        HEALTH_INSURANCE = "health_insurance", "Health Insurance"
        LIFE_INSURANCE = "life_insurance", "Life Insurance"
        LOAN = "loan", "Loan Repayment"
        ADVANCE = "advance", "Salary Advance"
        LATE_PENALTY = "late_penalty", "Late Penalty"
        ABSENCE = "absence", "Absence Deduction"
        OTHER = "other", "Other"

    salary = models.ForeignKey(
        EmployeeSalary,
        on_delete=models.CASCADE,
        related_name="deductions",
        help_text="The salary record this deduction belongs to"
    )

    deduction_type = models.CharField(
        max_length=20,
        choices=DeductionType.choices,
        default=DeductionType.OTHER,
        help_text="Type of deduction"
    )

    name = models.CharField(
        max_length=100,
        help_text="Name/description of the deduction"
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        help_text="Deduction amount"
    )

    class Meta:
        db_table = "salary_deduction"
        verbose_name = "Salary Deduction"
        verbose_name_plural = "Salary Deductions"
        ordering = ["deduction_type", "name"]

    def __str__(self):
        return f"{self.name}: {self.amount}"

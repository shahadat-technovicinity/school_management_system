"""
Salary Management Serializers

Comprehensive serializers for:
- Salary CRUD operations with nested allowances/deductions
- Dashboard aggregation
- Payment history
- Export functionality
"""

from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from datetime import datetime

from .models import EmployeeSalary, SalaryAllowance, SalaryDeduction
from teacher.models import Teacher


# ─────────────────────────────────────────────────────────────────────────────
# Nested Serializers for Allowances and Deductions
# ─────────────────────────────────────────────────────────────────────────────

class SalaryAllowanceSerializer(serializers.ModelSerializer):
    """Serializer for salary allowances."""
    allowance_type_display = serializers.CharField(
        source="get_allowance_type_display",
        read_only=True
    )

    class Meta:
        model = SalaryAllowance
        fields = [
            "id",
            "allowance_type",
            "allowance_type_display",
            "name",
            "amount",
        ]
        read_only_fields = ["id"]


class SalaryDeductionSerializer(serializers.ModelSerializer):
    """Serializer for salary deductions."""
    deduction_type_display = serializers.CharField(
        source="get_deduction_type_display",
        read_only=True
    )

    class Meta:
        model = SalaryDeduction
        fields = [
            "id",
            "deduction_type",
            "deduction_type_display",
            "name",
            "amount",
        ]
        read_only_fields = ["id"]


class AllowanceInputSerializer(serializers.Serializer):
    """Input serializer for creating/updating allowances."""
    allowance_type = serializers.ChoiceField(
        choices=SalaryAllowance.AllowanceType.choices,
        default=SalaryAllowance.AllowanceType.OTHER
    )
    name = serializers.CharField(max_length=100)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.00"))


class DeductionInputSerializer(serializers.Serializer):
    """Input serializer for creating/updating deductions."""
    deduction_type = serializers.ChoiceField(
        choices=SalaryDeduction.DeductionType.choices,
        default=SalaryDeduction.DeductionType.OTHER
    )
    name = serializers.CharField(max_length=100)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal("0.00"))


# ─────────────────────────────────────────────────────────────────────────────
# Employee Info Serializers (for nested display)
# ─────────────────────────────────────────────────────────────────────────────

class EmployeeBasicInfoSerializer(serializers.ModelSerializer):
    """Basic employee info for salary list."""
    name = serializers.CharField(source="user.name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    department = serializers.CharField(source="subject", read_only=True)  # Using subject as department
    position = serializers.CharField(source="qualification", read_only=True)  # Using qualification as position
    employment_type = serializers.CharField(source="contract_type", read_only=True)

    class Meta:
        model = Teacher
        fields = [
            "id",
            "teacher_id",
            "name",
            "email",
            "department",
            "position",
            "employment_type",
        ]


class EmployeeDetailInfoSerializer(serializers.ModelSerializer):
    """Detailed employee info for salary details."""
    name = serializers.CharField(source="user.name", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    phone = serializers.CharField(source="primary_contact_number", read_only=True)
    profile_picture = serializers.ImageField(source="photo", read_only=True)
    department = serializers.CharField(source="subject", read_only=True)
    position = serializers.CharField(source="qualification", read_only=True)
    employment_type = serializers.CharField(source="contract_type", read_only=True)
    joining_date = serializers.DateField(source="date_of_joining", read_only=True)

    class Meta:
        model = Teacher
        fields = [
            "id",
            "teacher_id",
            "name",
            "email",
            "phone",
            "profile_picture",
            "department",
            "position",
            "employment_type",
            "joining_date",
        ]


# ─────────────────────────────────────────────────────────────────────────────
# Salary List Serializer
# ─────────────────────────────────────────────────────────────────────────────

class SalaryListSerializer(serializers.ModelSerializer):
    """
    Serializer for salary list view.
    Shows summary info for each salary record.
    """
    employee_name = serializers.CharField(source="employee.user.name", read_only=True)
    employee_id = serializers.CharField(source="employee.teacher_id", read_only=True)
    department = serializers.CharField(source="employee.subject", read_only=True)  # Using subject as department
    position = serializers.CharField(source="employee.qualification", read_only=True)  # Using qualification as position
    
    # Computed fields
    total_allowances = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    total_deductions = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    net_salary = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    
    # Display fields
    payment_status_display = serializers.CharField(
        source="get_payment_status_display",
        read_only=True
    )
    month_display = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeSalary
        fields = [
            "id",
            "employee_name",
            "employee_id",
            "department",
            "position",
            "month",
            "month_display",
            "basic_salary",
            "total_allowances",
            "total_deductions",
            "net_salary",
            "payment_status",
            "payment_status_display",
            "payment_date",
        ]

    def get_month_display(self, obj) -> str:
        return obj.month.strftime("%B %Y")


# ─────────────────────────────────────────────────────────────────────────────
# Salary Detail Serializer
# ─────────────────────────────────────────────────────────────────────────────

class PaymentHistorySerializer(serializers.Serializer):
    """Serializer for payment history entries."""
    month = serializers.DateField()
    month_display = serializers.SerializerMethodField()
    net_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    payment_status = serializers.CharField()
    payment_status_display = serializers.CharField()
    payment_date = serializers.DateTimeField()

    def get_month_display(self, obj) -> str:
        if isinstance(obj.get("month"), datetime):
            return obj["month"].strftime("%B %Y")
        return obj.get("month", "").strftime("%B %Y") if obj.get("month") else ""


class SalaryDetailSerializer(serializers.ModelSerializer):
    """
    Full salary details including employee info, breakdown, and history.
    """
    # Employee info
    employee = EmployeeDetailInfoSerializer(read_only=True)
    
    # Nested components
    allowances = SalaryAllowanceSerializer(many=True, read_only=True)
    deductions = SalaryDeductionSerializer(many=True, read_only=True)
    
    # Computed fields
    total_allowances = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    total_deductions = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    net_salary = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    gross_salary = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    
    # Display fields
    payment_status_display = serializers.CharField(
        source="get_payment_status_display",
        read_only=True
    )
    payment_frequency_display = serializers.CharField(
        source="get_payment_frequency_display",
        read_only=True
    )
    payment_method_display = serializers.CharField(
        source="get_payment_method_display",
        read_only=True
    )
    month_display = serializers.SerializerMethodField()
    
    # Payment history (last 6 months)
    payment_history = serializers.SerializerMethodField()

    class Meta:
        model = EmployeeSalary
        fields = [
            "id",
            "employee",
            "month",
            "month_display",
            "basic_salary",
            "payment_frequency",
            "payment_frequency_display",
            "payment_method",
            "payment_method_display",
            "payment_status",
            "payment_status_display",
            "payment_date",
            "comments",
            "allowances",
            "deductions",
            "total_allowances",
            "total_deductions",
            "gross_salary",
            "net_salary",
            "payment_history",
            "created_at",
            "updated_at",
        ]

    def get_month_display(self, obj) -> str:
        return obj.month.strftime("%B %Y")

    def get_payment_history(self, obj) -> list:
        """Get last 6 months of payment history for this employee."""
        history = EmployeeSalary.objects.filter(
            employee=obj.employee
        ).exclude(
            id=obj.id
        ).order_by("-month")[:6]

        return [
            {
                "month": item.month,
                "month_display": item.month.strftime("%B %Y"),
                "net_salary": item.net_salary,
                "payment_status": item.payment_status,
                "payment_status_display": item.get_payment_status_display(),
                "payment_date": item.payment_date,
            }
            for item in history
        ]


# ─────────────────────────────────────────────────────────────────────────────
# Salary Create Serializer
# ─────────────────────────────────────────────────────────────────────────────

class SalaryCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new salary record.
    Supports nested allowances and deductions.
    """
    allowances = AllowanceInputSerializer(many=True, required=False, default=[])
    deductions = DeductionInputSerializer(many=True, required=False, default=[])
    
    # Accept month as YYYY-MM string or date
    month = serializers.DateField(
        input_formats=["%Y-%m-%d", "%Y-%m"],
        help_text="Salary month in format YYYY-MM or YYYY-MM-DD"
    )

    class Meta:
        model = EmployeeSalary
        fields = [
            "employee",
            "month",
            "basic_salary",
            "payment_frequency",
            "payment_method",
            "comments",
            "allowances",
            "deductions",
        ]

    def validate_month(self, value):
        """Normalize month to first day of month."""
        return value.replace(day=1)

    def validate(self, attrs):
        """Check for duplicate salary record."""
        employee = attrs.get("employee")
        month = attrs.get("month")

        if EmployeeSalary.objects.filter(employee=employee, month=month).exists():
            raise serializers.ValidationError({
                "month": f"Salary record for {month.strftime('%B %Y')} already exists for this employee."
            })

        return attrs

    @transaction.atomic
    def create(self, validated_data):
        """Create salary with nested allowances and deductions."""
        allowances_data = validated_data.pop("allowances", [])
        deductions_data = validated_data.pop("deductions", [])

        # Add created_by if available
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            validated_data["created_by"] = request.user

        salary = EmployeeSalary.objects.create(**validated_data)

        # Create allowances
        for allowance_data in allowances_data:
            SalaryAllowance.objects.create(salary=salary, **allowance_data)

        # Create deductions
        for deduction_data in deductions_data:
            SalaryDeduction.objects.create(salary=salary, **deduction_data)

        return salary


# ─────────────────────────────────────────────────────────────────────────────
# Salary Update Serializer
# ─────────────────────────────────────────────────────────────────────────────

class SalaryUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating a salary record.
    Replaces all allowances and deductions with new data.
    """
    allowances = AllowanceInputSerializer(many=True, required=False)
    deductions = DeductionInputSerializer(many=True, required=False)

    class Meta:
        model = EmployeeSalary
        fields = [
            "basic_salary",
            "payment_frequency",
            "payment_method",
            "comments",
            "allowances",
            "deductions",
        ]

    @transaction.atomic
    def update(self, instance, validated_data):
        """Update salary with nested allowances and deductions."""
        allowances_data = validated_data.pop("allowances", None)
        deductions_data = validated_data.pop("deductions", None)

        # Update main salary fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Replace allowances if provided
        if allowances_data is not None:
            instance.allowances.all().delete()
            for allowance_data in allowances_data:
                SalaryAllowance.objects.create(salary=instance, **allowance_data)

        # Replace deductions if provided
        if deductions_data is not None:
            instance.deductions.all().delete()
            for deduction_data in deductions_data:
                SalaryDeduction.objects.create(salary=instance, **deduction_data)

        return instance


# ─────────────────────────────────────────────────────────────────────────────
# Payment Action Serializer
# ─────────────────────────────────────────────────────────────────────────────

class SalaryPaymentSerializer(serializers.Serializer):
    """Serializer for processing salary payment."""
    action = serializers.ChoiceField(
        choices=["pay", "cancel"],
        help_text="Action to perform: 'pay' or 'cancel'"
    )
    payment_method = serializers.ChoiceField(
        choices=EmployeeSalary.PaymentMethod.choices,
        required=False,
        help_text="Override payment method (optional)"
    )
    comments = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Additional comments for the payment"
    )

    def validate(self, attrs):
        salary = self.context.get("salary")
        action = attrs.get("action")

        if action == "pay" and salary.payment_status == "paid":
            raise serializers.ValidationError({
                "action": "This salary has already been paid."
            })

        if action == "cancel" and salary.payment_status == "paid":
            raise serializers.ValidationError({
                "action": "Cannot cancel a paid salary. Contact admin for refund."
            })

        return attrs

    def save(self, **kwargs):
        salary = kwargs.get("salary")
        user = kwargs.get("user")
        action = self.validated_data.get("action")

        if action == "pay":
            salary.payment_status = "paid"
            salary.payment_date = timezone.now()
            if user:
                salary.paid_by = user
            if self.validated_data.get("payment_method"):
                salary.payment_method = self.validated_data["payment_method"]

        elif action == "cancel":
            salary.payment_status = "cancelled"

        if self.validated_data.get("comments"):
            if salary.comments:
                salary.comments += f"\n[Payment Note] {self.validated_data['comments']}"
            else:
                salary.comments = f"[Payment Note] {self.validated_data['comments']}"

        salary.save()
        return salary


# ─────────────────────────────────────────────────────────────────────────────
# Dashboard Serializers
# ─────────────────────────────────────────────────────────────────────────────

class SalaryDashboardSerializer(serializers.Serializer):
    """Serializer for salary dashboard metrics."""
    # Current month metrics
    total_salary_disbursement = serializers.DecimalField(max_digits=15, decimal_places=2)
    disbursement_change_percent = serializers.DecimalField(max_digits=6, decimal_places=2)
    
    total_employees = serializers.IntegerField()
    employees_change_percent = serializers.DecimalField(max_digits=6, decimal_places=2)
    
    average_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_change_percent = serializers.DecimalField(max_digits=6, decimal_places=2)
    
    pending_approvals = serializers.IntegerField()
    paid_count = serializers.IntegerField()
    
    # Additional metrics
    total_allowances = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_deductions = serializers.DecimalField(max_digits=15, decimal_places=2)
    
    # Month info
    current_month = serializers.DateField()
    current_month_display = serializers.CharField()


# ─────────────────────────────────────────────────────────────────────────────
# Export Serializer
# ─────────────────────────────────────────────────────────────────────────────

class SalaryExportSerializer(serializers.ModelSerializer):
    """Serializer for exporting salary data to CSV/Excel."""
    employee_name = serializers.CharField(source="employee.user.name")
    employee_id = serializers.CharField(source="employee.teacher_id")
    department = serializers.CharField(source="employee.subject")
    position = serializers.CharField(source="employee.qualification")
    employment_type = serializers.CharField(source="employee.contract_type")
    month_display = serializers.SerializerMethodField()
    total_allowances = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_deductions = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    payment_status_display = serializers.CharField(source="get_payment_status_display")
    payment_method_display = serializers.CharField(source="get_payment_method_display")

    class Meta:
        model = EmployeeSalary
        fields = [
            "employee_id",
            "employee_name",
            "department",
            "position",
            "employment_type",
            "month_display",
            "basic_salary",
            "total_allowances",
            "total_deductions",
            "net_salary",
            "payment_status_display",
            "payment_method_display",
            "payment_date",
        ]

    def get_month_display(self, obj) -> str:
        return obj.month.strftime("%B %Y")


# ─────────────────────────────────────────────────────────────────────────────
# Bulk Payment Serializer
# ─────────────────────────────────────────────────────────────────────────────

class BulkPaymentSerializer(serializers.Serializer):
    """Serializer for processing bulk salary payments."""
    salary_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        help_text="List of salary IDs to process payment for"
    )
    payment_method = serializers.ChoiceField(
        choices=EmployeeSalary.PaymentMethod.choices,
        required=False,
        help_text="Override payment method for all (optional)"
    )

    def validate_salary_ids(self, value):
        """Validate that all salary IDs exist and are pending."""
        existing_ids = set(
            EmployeeSalary.objects.filter(id__in=value).values_list("id", flat=True)
        )
        missing = set(value) - existing_ids
        if missing:
            raise serializers.ValidationError(
                f"Salary records not found: {list(missing)}"
            )

        already_paid = EmployeeSalary.objects.filter(
            id__in=value,
            payment_status="paid"
        ).values_list("id", flat=True)

        if already_paid:
            raise serializers.ValidationError(
                f"Some salaries are already paid: {list(already_paid)}"
            )

        return value

    @transaction.atomic
    def save(self, **kwargs):
        user = kwargs.get("user")
        salary_ids = self.validated_data["salary_ids"]
        payment_method = self.validated_data.get("payment_method")

        update_fields = {
            "payment_status": "paid",
            "payment_date": timezone.now(),
        }
        if user:
            update_fields["paid_by"] = user
        if payment_method:
            update_fields["payment_method"] = payment_method

        updated = EmployeeSalary.objects.filter(
            id__in=salary_ids,
            payment_status="pending"
        ).update(**update_fields)

        return {
            "processed": updated,
            "total_requested": len(salary_ids)
        }

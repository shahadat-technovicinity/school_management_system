"""
Salary Management Admin

Django admin configuration for salary models.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import EmployeeSalary, SalaryAllowance, SalaryDeduction


class SalaryAllowanceInline(admin.TabularInline):
    """Inline admin for salary allowances."""
    model = SalaryAllowance
    extra = 1
    fields = ["allowance_type", "name", "amount"]


class SalaryDeductionInline(admin.TabularInline):
    """Inline admin for salary deductions."""
    model = SalaryDeduction
    extra = 1
    fields = ["deduction_type", "name", "amount"]


@admin.register(EmployeeSalary)
class EmployeeSalaryAdmin(admin.ModelAdmin):
    """Admin for employee salaries."""
    list_display = [
        "id",
        "employee_name",
        "employee_id_display",
        "department",
        "month_display",
        "basic_salary",
        "net_salary_display",
        "payment_status_badge",
        "payment_date",
    ]
    list_filter = [
        "payment_status",
        "payment_method",
        "payment_frequency",
        "month",
        "employee__role",
    ]
    search_fields = [
        "employee__name",
        "employee__username",
        "employee__phone_number",
    ]
    date_hierarchy = "month"
    ordering = ["-month", "-created_at"]
    readonly_fields = [
        "created_at",
        "updated_at",
        "net_salary_display",
        "total_allowances_display",
        "total_deductions_display",
    ]
    inlines = [SalaryAllowanceInline, SalaryDeductionInline]
    
    fieldsets = (
        ("Employee Information", {
            "fields": ("employee",)
        }),
        ("Salary Details", {
            "fields": (
                "month",
                "basic_salary",
                "payment_frequency",
                "payment_method",
            )
        }),
        ("Computed Values", {
            "fields": (
                "total_allowances_display",
                "total_deductions_display",
                "net_salary_display",
            ),
            "classes": ("collapse",)
        }),
        ("Payment Status", {
            "fields": (
                "payment_status",
                "payment_date",
                "paid_by",
            )
        }),
        ("Additional Info", {
            "fields": (
                "comments",
                "created_by",
                "created_at",
                "updated_at",
            ),
            "classes": ("collapse",)
        }),
    )

    def employee_name(self, obj):
        return obj.employee.name
    employee_name.short_description = "Employee"
    employee_name.admin_order_field = "employee__name"

    def employee_id_display(self, obj):
        return obj.employee.username
    employee_id_display.short_description = "Employee ID"

    def department(self, obj):
        return obj.employee.role or "-"
    department.admin_order_field = "employee__role"

    def month_display(self, obj):
        return obj.month.strftime("%B %Y")
    month_display.short_description = "Month"
    month_display.admin_order_field = "month"

    def net_salary_display(self, obj):
        return f"${obj.net_salary:,.2f}"
    net_salary_display.short_description = "Net Salary"

    def total_allowances_display(self, obj):
        return f"${obj.total_allowances:,.2f}"
    total_allowances_display.short_description = "Total Allowances"

    def total_deductions_display(self, obj):
        return f"${obj.total_deductions:,.2f}"
    total_deductions_display.short_description = "Total Deductions"

    def payment_status_badge(self, obj):
        colors = {
            "pending": "#ffc107",
            "paid": "#28a745",
            "processing": "#17a2b8",
            "cancelled": "#dc3545",
        }
        color = colors.get(obj.payment_status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_payment_status_display()
        )
    payment_status_badge.short_description = "Status"
    payment_status_badge.admin_order_field = "payment_status"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "employee", "created_by", "paid_by"
        ).prefetch_related("allowances", "deductions")


@admin.register(SalaryAllowance)
class SalaryAllowanceAdmin(admin.ModelAdmin):
    """Admin for salary allowances."""
    list_display = ["id", "salary", "allowance_type", "name", "amount"]
    list_filter = ["allowance_type"]
    search_fields = ["name", "salary__employee__name"]
    ordering = ["-salary__month", "allowance_type"]


@admin.register(SalaryDeduction)
class SalaryDeductionAdmin(admin.ModelAdmin):
    """Admin for salary deductions."""
    list_display = ["id", "salary", "deduction_type", "name", "amount"]
    list_filter = ["deduction_type"]
    search_fields = ["name", "salary__employee__name"]
    ordering = ["-salary__month", "deduction_type"]

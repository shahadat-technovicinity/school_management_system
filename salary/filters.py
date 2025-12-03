"""
Salary Management Filters

Django-filter backends for filtering salary records.
"""

import django_filters
from django.db.models import Q
from datetime import datetime

from .models import EmployeeSalary


class SalaryFilter(django_filters.FilterSet):
    """
    Filter for salary list with support for:
    - Month filtering (YYYY-MM format)
    - Department (subject)
    - Staff category
    - Employment type (contract_type)
    - Payment status
    - Employee search
    """

    # Month filter (accepts YYYY-MM format)
    month = django_filters.CharFilter(method="filter_month")
    
    # Department filter (mapped to subject in Teacher model)
    department = django_filters.CharFilter(
        field_name="employee__subject",
        lookup_expr="icontains"
    )
    
    # Position filter (mapped to qualification)
    position = django_filters.CharFilter(
        field_name="employee__qualification",
        lookup_expr="icontains"
    )
    
    # Employment type filter (mapped to contract_type: permanent, contract, temporary, part_time)
    employment_type = django_filters.CharFilter(
        field_name="employee__contract_type",
        lookup_expr="iexact"
    )
    
    # Staff category filter (class_assigned as proxy)
    staff_category = django_filters.CharFilter(
        field_name="employee__class_assigned",
        lookup_expr="icontains"
    )
    
    # Payment status filter
    payment_status = django_filters.ChoiceFilter(
        choices=EmployeeSalary.PaymentStatus.choices
    )
    
    # Payment method filter
    payment_method = django_filters.ChoiceFilter(
        choices=EmployeeSalary.PaymentMethod.choices
    )
    
    # Employee ID filter (exact match)
    employee_id = django_filters.NumberFilter(
        field_name="employee__id"
    )
    
    # Teacher ID filter (e.g., EMP-2025-001)
    teacher_id = django_filters.CharFilter(
        field_name="employee__teacher_id",
        lookup_expr="icontains"
    )
    
    # Search filter (name, email, teacher_id)
    search = django_filters.CharFilter(method="filter_search")
    
    # Date range filters
    from_month = django_filters.CharFilter(method="filter_from_month")
    to_month = django_filters.CharFilter(method="filter_to_month")
    
    # Salary range filters
    min_salary = django_filters.NumberFilter(
        field_name="basic_salary",
        lookup_expr="gte"
    )
    max_salary = django_filters.NumberFilter(
        field_name="basic_salary",
        lookup_expr="lte"
    )

    class Meta:
        model = EmployeeSalary
        fields = [
            "month",
            "department",
            "position",
            "employment_type",
            "staff_category",
            "payment_status",
            "payment_method",
            "employee_id",
            "teacher_id",
            "search",
            "from_month",
            "to_month",
            "min_salary",
            "max_salary",
        ]

    def filter_month(self, queryset, name, value):
        """Filter by month in YYYY-MM format."""
        try:
            # Parse YYYY-MM format
            if "-" in value and len(value) == 7:
                year, month = value.split("-")
                date = datetime(int(year), int(month), 1).date()
                return queryset.filter(month=date)
            # Parse "May 2025" format
            else:
                date = datetime.strptime(value, "%B %Y").date()
                return queryset.filter(month=date.replace(day=1))
        except (ValueError, AttributeError):
            return queryset

    def filter_from_month(self, queryset, name, value):
        """Filter salaries from this month onwards."""
        try:
            if "-" in value and len(value) == 7:
                year, month = value.split("-")
                date = datetime(int(year), int(month), 1).date()
                return queryset.filter(month__gte=date)
        except (ValueError, AttributeError):
            pass
        return queryset

    def filter_to_month(self, queryset, name, value):
        """Filter salaries up to this month."""
        try:
            if "-" in value and len(value) == 7:
                year, month = value.split("-")
                date = datetime(int(year), int(month), 1).date()
                return queryset.filter(month__lte=date)
        except (ValueError, AttributeError):
            pass
        return queryset

    def filter_search(self, queryset, name, value):
        """
        Search across employee name, email, and teacher_id.
        """
        if not value:
            return queryset
        
        return queryset.filter(
            Q(employee__user__name__icontains=value) |
            Q(employee__user__email__icontains=value) |
            Q(employee__teacher_id__icontains=value)
        )

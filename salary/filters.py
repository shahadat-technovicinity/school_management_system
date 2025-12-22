"""
Salary Management Filters

Django-filter backends for filtering salary records.
"""

import django_filters
from django.db.models import Q

from .models import EmployeeSalary


class SalaryFilter(django_filters.FilterSet):
    """
    Filter for salary list with support for:
    - Department filtering
    - Position filtering
    - Payment status
    - Employee search
    """
    
    # Department filter
    department = django_filters.CharFilter(
        field_name="department",
        lookup_expr="icontains"
    )
    
    # Position filter
    position = django_filters.CharFilter(
        field_name="position",
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
    
    # Employee username filter
    employee_username = django_filters.CharFilter(
        field_name="employee__username",
        lookup_expr="icontains"
    )
    
    # Search filter (name, email, username, phone)
    search = django_filters.CharFilter(method="filter_search")
    
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
            "department",
            "position",
            "payment_status",
            "payment_method",
            "employee_id",
            "employee_username",
            "search",
            "min_salary",
            "max_salary",
        ]

    def filter_search(self, queryset, name, value):
        """
        Search across employee name, username, phone, department, and position.
        """
        if not value:
            return queryset
        
        return queryset.filter(
            Q(employee__name__icontains=value) |
            Q(employee__username__icontains=value) |
            Q(employee__phone_number__icontains=value) |
            Q(department__icontains=value) |
            Q(position__icontains=value)
        )

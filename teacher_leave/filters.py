import django_filters
from .models import TeacherLeave, LeaveBalance


class TeacherLeaveFilter(django_filters.FilterSet):
    """Filter class for Teacher Leave applications."""
    
    # Date range filters
    from_date = django_filters.DateFilter(field_name="from_date", lookup_expr="gte")
    to_date = django_filters.DateFilter(field_name="to_date", lookup_expr="lte")
    applied_from = django_filters.DateFilter(field_name="applied_on", lookup_expr="gte")
    applied_to = django_filters.DateFilter(field_name="applied_on", lookup_expr="lte")
    
    # Year filter
    year = django_filters.NumberFilter(field_name="from_date", lookup_expr="year")
    
    # Status filter with multiple values
    status = django_filters.CharFilter(method="filter_status")
    
    # Teacher filter
    teacher = django_filters.NumberFilter(field_name="teacher_id")
    teacher_code = django_filters.CharFilter(
        field_name="teacher__teacher_id",
        lookup_expr="icontains"
    )
    
    # Leave type filter
    leave_type = django_filters.NumberFilter(field_name="leave_type_id")
    leave_type_name = django_filters.CharFilter(
        field_name="leave_type__name",
        lookup_expr="icontains"
    )

    class Meta:
        model = TeacherLeave
        fields = [
            "status",
            "teacher",
            "teacher_code",
            "leave_type",
            "leave_type_name",
            "from_date",
            "to_date",
            "applied_from",
            "applied_to",
            "year",
            "leave_days",
        ]

    def filter_status(self, queryset, name, value):
        """Allow filtering by multiple status values (comma-separated)."""
        if value:
            statuses = [s.strip() for s in value.split(",")]
            return queryset.filter(status__in=statuses)
        return queryset


class LeaveBalanceFilter(django_filters.FilterSet):
    """Filter class for Leave Balance."""
    
    teacher = django_filters.NumberFilter(field_name="teacher_id")
    leave_type = django_filters.NumberFilter(field_name="leave_type_id")
    year = django_filters.NumberFilter(field_name="year")
    
    class Meta:
        model = LeaveBalance
        fields = ["teacher", "leave_type", "year"]

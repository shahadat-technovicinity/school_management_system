import django_filters
from .models import Teacher


class TeacherFilter(django_filters.FilterSet):
    """
    Filter class for Teacher model.
    Provides various filtering options for the teacher list endpoint.
    """

    # Exact match filters
    status = django_filters.ChoiceFilter(choices=Teacher.STATUS_CHOICES)
    gender = django_filters.ChoiceFilter(choices=Teacher.GENDER_CHOICES)
    blood_group = django_filters.ChoiceFilter(choices=Teacher.BLOOD_GROUP_CHOICES)
    marital_status = django_filters.ChoiceFilter(choices=Teacher.MARITAL_STATUS_CHOICES)
    contract_type = django_filters.ChoiceFilter(choices=Teacher.CONTRACT_TYPE_CHOICES)
    work_shift = django_filters.ChoiceFilter(choices=Teacher.WORK_SHIFT_CHOICES)

    # Contains filters (case-insensitive)
    subject = django_filters.CharFilter(lookup_expr="icontains")
    class_assigned = django_filters.CharFilter(lookup_expr="icontains")
    qualification = django_filters.CharFilter(lookup_expr="icontains")
    work_location = django_filters.CharFilter(lookup_expr="icontains")

    # Date range filters
    date_of_joining_after = django_filters.DateFilter(
        field_name="date_of_joining",
        lookup_expr="gte",
        help_text="Filter teachers who joined on or after this date (YYYY-MM-DD)"
    )
    date_of_joining_before = django_filters.DateFilter(
        field_name="date_of_joining",
        lookup_expr="lte",
        help_text="Filter teachers who joined on or before this date (YYYY-MM-DD)"
    )

    # User-related filters
    user_name = django_filters.CharFilter(
        field_name="user__name",
        lookup_expr="icontains",
        help_text="Filter by user's name (partial match)"
    )

    # Boolean/Null filters
    has_resume = django_filters.BooleanFilter(
        field_name="resume",
        method="filter_has_file",
        help_text="Filter teachers who have uploaded a resume"
    )
    has_joining_letter = django_filters.BooleanFilter(
        field_name="joining_letter",
        method="filter_has_file",
        help_text="Filter teachers who have uploaded a joining letter"
    )

    class Meta:
        model = Teacher
        fields = [
            "status",
            "gender",
            "blood_group",
            "marital_status",
            "contract_type",
            "work_shift",
            "subject",
            "class_assigned",
            "qualification",
            "work_location",
            "date_of_joining_after",
            "date_of_joining_before",
            "user_name",
            "has_resume",
            "has_joining_letter",
        ]

    def filter_has_file(self, queryset, name, value):
        """Filter by whether a file field is empty or not."""
        if value is True:
            return queryset.exclude(**{f"{name}": ""}).exclude(**{f"{name}": None})
        elif value is False:
            return queryset.filter(**{f"{name}__in": ["", None]})
        return queryset

import django_filters
from django.db.models import Q
from .models import TeacherAndStaffProfile


class TeacherAndStaffFilter(django_filters.FilterSet):
    """
    Filter class for TeacherAndStaffProfile model.
    """

    # Primary Categorization
    employee_type = django_filters.ChoiceFilter(
        choices=TeacherAndStaffProfile.EMPLOYEE_TYPE_CHOICES,
        help_text="Filter by employee type (e.g., teacher, staff)"
    )
    status = django_filters.ChoiceFilter(choices=TeacherAndStaffProfile.STATUS_CHOICES)
    gender = django_filters.ChoiceFilter(choices=TeacherAndStaffProfile.GENDER_CHOICES)
    blood_group = django_filters.ChoiceFilter(choices=TeacherAndStaffProfile.BLOOD_GROUP_CHOICES)
    marital_status = django_filters.ChoiceFilter(choices=TeacherAndStaffProfile.MARITAL_STATUS_CHOICES)
    contract_type = django_filters.ChoiceFilter(choices=TeacherAndStaffProfile.CONTRACT_TYPE_CHOICES)
    work_shift = django_filters.ChoiceFilter(choices=TeacherAndStaffProfile.WORK_SHIFT_CHOICES)

    # Text Searches
    designation = django_filters.CharFilter(lookup_expr="icontains")
    department = django_filters.CharFilter(lookup_expr="icontains")
    qualification = django_filters.CharFilter(lookup_expr="icontains")
    work_location = django_filters.CharFilter(lookup_expr="icontains")
    district = django_filters.CharFilter(lookup_expr="icontains")
    nid_number = django_filters.CharFilter(lookup_expr="icontains")
    primary_contact_number = django_filters.CharFilter(lookup_expr="icontains")

    # Name Searches
    user_name = django_filters.CharFilter(
        field_name="user__name",
        lookup_expr="icontains",
        help_text="Filter by user's English name (partial match)"
    )
    name_bn = django_filters.CharFilter(
        lookup_expr="icontains",
        help_text="Filter by Bangla name (partial match)"
    )

    # Universal Search Bar Parameter
    search = django_filters.CharFilter(
        method="filter_by_search",
        help_text="Search across name, phone number, designation, and NID number"
    )

    # Date Filters
    date_of_joining_after = django_filters.DateFilter(
        field_name="date_of_joining",
        lookup_expr="gte",
        help_text="Filter employees who joined on or after this date (YYYY-MM-DD)"
    )
    date_of_joining_before = django_filters.DateFilter(
        field_name="date_of_joining",
        lookup_expr="lte",
        help_text="Filter employees who joined on or before this date (YYYY-MM-DD)"
    )

    # File Upload Checks
    has_resume = django_filters.BooleanFilter(
        field_name="resume",
        method="filter_has_file",
        help_text="Filter employees who have uploaded a resume"
    )
    has_joining_letter = django_filters.BooleanFilter(
        field_name="joining_letter",
        method="filter_has_file",
        help_text="Filter employees who have uploaded a joining letter"
    )

    class Meta:
        model = TeacherAndStaffProfile
        fields = [
            "employee_type", "status", "gender", "blood_group", 
            "marital_status", "contract_type", "work_shift"
        ]

    def filter_has_file(self, queryset, name, value):
        """Filter by whether a file field is empty or not."""
        if value is True:
            return queryset.exclude(**{f"{name}": ""}).exclude(**{f"{name}__isnull": True})
        elif value is False:
            return queryset.filter(Q(**{f"{name}": ""}) | Q(**{f"{name}__isnull": True}))
        return queryset

    def filter_by_search(self, queryset, name, value):
        """Search across multiple text fields simultaneously."""
        if not value:
            return queryset
        return queryset.filter(
            Q(user__name__icontains=value) |
            Q(name_bn__icontains=value) |
            Q(primary_contact_number__icontains=value) |
            Q(designation__icontains=value) |
            Q(nid_number__icontains=value)
        )
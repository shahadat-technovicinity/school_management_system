import django_filters
from django.db.models import Q
from .models import Teacher


class TeacherFilter(django_filters.FilterSet):
    """
    Filter class for Teacher model.
    """

    status = django_filters.ChoiceFilter(choices=Teacher.STATUS_CHOICES)
    gender = django_filters.ChoiceFilter(choices=Teacher.GENDER_CHOICES)
    blood_group = django_filters.ChoiceFilter(choices=Teacher.BLOOD_GROUP_CHOICES)
    marital_status = django_filters.ChoiceFilter(choices=Teacher.MARITAL_STATUS_CHOICES)
    contract_type = django_filters.ChoiceFilter(choices=Teacher.CONTRACT_TYPE_CHOICES)
    work_shift = django_filters.ChoiceFilter(choices=Teacher.WORK_SHIFT_CHOICES)

    # Subject Filtering
    subject = django_filters.NumberFilter(
        field_name="subject__id",
        help_text="Filter by subject ID"
    )
    subject_name = django_filters.CharFilter(
        field_name="subject__name",
        lookup_expr="icontains",
        help_text="Filter by subject name (partial match)"
    )

    # Class Filtering
    class_assigned = django_filters.NumberFilter(
        field_name="class_assigned__id",
        help_text="Filter by class ID"
    )
    class_name = django_filters.CharFilter(
        field_name="class_assigned__name",
        lookup_expr="icontains",
        help_text="Filter by class name (partial match)"
    )

    # Text Searches
    qualification = django_filters.CharFilter(lookup_expr="icontains")
    work_location = django_filters.CharFilter(lookup_expr="icontains")
    district = django_filters.CharFilter(lookup_expr="icontains")
    nid_number = django_filters.CharFilter(lookup_expr="icontains")
    
    # Name searches
    user_name = django_filters.CharFilter(
        field_name="user__name",
        lookup_expr="icontains",
        help_text="Filter by user's English name (partial match)"
    )
    name_bn = django_filters.CharFilter(
        lookup_expr="icontains",
        help_text="Filter by teacher's Bangla name (partial match)"
    )

    # Date Filters
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

    # File Checks
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
        # 🟢 Meta.fields শুধুমাত্র মডেলে সরাসরি থাকা নির্দিষ্ট ডিরেক্ট ফিল্ডগুলোতেই সীমাবদ্ধ রাখুন
        fields = [
            "status", "gender", "blood_group", "marital_status",
            "contract_type", "work_shift",
        ]

    def filter_has_file(self, queryset, name, value):
        """Filter by whether a file field is empty or not."""
        if value is True:
            return queryset.exclude(**{f"{name}": ""}).exclude(**{f"{name}__isnull": True})
        elif value is False:
            return queryset.filter(Q(**{f"{name}": ""}) | Q(**{f"{name}__isnull": True}))
        return queryset
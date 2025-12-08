from django.contrib import admin
from .models import Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    """Admin configuration for Teacher model."""

    list_display = (
        "teacher_id",
        "get_user_name",
        "subject",
        "class_assigned",
        "status",
        "date_of_joining",
        "created_at",
    )
    list_filter = (
        "status",
        "gender",
        "contract_type",
        "work_shift",
        "marital_status",
    )
    search_fields = (
        "teacher_id",
        "user__name",
        "user__username",
        "subject",
        "class_assigned",
        "primary_contact_number",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    list_per_page = 25

    fieldsets = (
        ("User Link", {
            "fields": ("user",),
        }),
        ("Personal Information", {
            "fields": (
                "teacher_id",
                "gender",
                "date_of_birth",
                "marital_status",
                "blood_group",
                "primary_contact_number",
                "languages_known",
            ),
        }),
        ("Family", {
            "fields": ("father_name", "mother_name"),
        }),
        ("Professional", {
            "fields": (
                "class_assigned",
                "subject",
                "qualification",
                "work_experience",
            ),
        }),
        ("Previous Employment", {
            "fields": (
                "previous_school_name",
                "previous_school_address",
                "previous_school_phone",
            ),
            "classes": ("collapse",),
        }),
        ("Address", {
            "fields": ("permanent_address", "current_address"),
        }),
        ("Payroll", {
            "fields": (
                "basic_salary",
                "epf_no",
                "pan_number",
                "contract_type",
                "work_shift",
                "work_location",
                "date_of_joining",
                "date_of_leaving",
            ),
        }),
        ("Leave Allocation", {
            "fields": (
                "medical_leaves",
                "casual_leaves",
                "maternity_leaves",
                "sick_leaves",
            ),
            "classes": ("collapse",),
        }),
        ("Bank Details", {
            "fields": (
                "account_name",
                "account_number",
                "bank_name",
                "branch_name",
                "ifsc_code",
            ),
            "classes": ("collapse",),
        }),
        ("Transport", {
            "fields": ("route_id", "vehicle_number", "pickup_point"),
            "classes": ("collapse",),
        }),
        ("Hostel", {
            "fields": ("hostel_id", "room_no"),
            "classes": ("collapse",),
        }),
        ("Social Media", {
            "fields": ("facebook", "instagram", "linkedin", "youtube", "twitter"),
            "classes": ("collapse",),
        }),
        ("Documents", {
            "fields": ("photo", "resume", "joining_letter"),
        }),
        ("Additional", {
            "fields": ("status", "notes"),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    def get_user_name(self, obj):
        """Return the linked user's name."""
        return obj.user.name if obj.user else "-"
    get_user_name.short_description = "Name"
    get_user_name.admin_order_field = "user__name"

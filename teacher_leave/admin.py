from django.contrib import admin
from .models import LeaveType, LeaveBalance, TeacherLeave


@admin.register(LeaveType)
class LeaveTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "default_days", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["name", "description"]
    ordering = ["name"]


@admin.register(LeaveBalance)
class LeaveBalanceAdmin(admin.ModelAdmin):
    list_display = ["teacher", "leave_type", "year", "total_allocated", "used", "available"]
    list_filter = ["year", "leave_type"]
    search_fields = ["teacher__teacher_id", "teacher__user__name"]
    ordering = ["-year", "teacher"]

    def available(self, obj):
        return obj.available
    available.short_description = "Available"


@admin.register(TeacherLeave)
class TeacherLeaveAdmin(admin.ModelAdmin):
    list_display = [
        "teacher", "leave_type", "from_date", "to_date",
        "no_of_days", "status", "applied_on"
    ]
    list_filter = ["status", "leave_type", "applied_on"]
    search_fields = ["teacher__teacher_id", "teacher__user__name", "reason"]
    ordering = ["-applied_on"]
    readonly_fields = ["applied_on", "created_at", "updated_at"]
    
    fieldsets = (
        ("Leave Application", {
            "fields": (
                "teacher", "leave_type", "leave_date",
                "from_date", "to_date", "leave_days", "no_of_days", "reason"
            )
        }),
        ("Status", {
            "fields": ("status", "reviewed_by", "reviewed_at", "admin_remarks")
        }),
        ("Timestamps", {
            "fields": ("applied_on", "created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

from django.contrib import admin
from .models import Teacher


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("teacher_id", "first_name", "last_name", "subject", "class_assigned", "status")
    list_filter = ("status", "gender")
    search_fields = ("teacher_id", "first_name", "last_name", "email")

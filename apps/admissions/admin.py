from django.contrib import admin
from .models import (
    StudentAdmission,
    PreviousAcademicRecord,
    AdmissionSkill,
    AdmissionSkillLink,
    LotterySession,
    AdmissionDocument
)

@admin.register(StudentAdmission)
class StudentAdmissionAdmin(admin.ModelAdmin):
    list_display = ('student_name_english', 'application_number', 'desired_class', 'admission_status')
    search_fields = ('student_name_english', 'application_number', 'mobile_number')
    list_filter = ('admission_status', 'desired_class', 'gender')

admin.site.register(PreviousAcademicRecord)
admin.site.register(AdmissionSkill)
admin.site.register(AdmissionSkillLink)
admin.site.register(LotterySession)
admin.site.register(AdmissionDocument)

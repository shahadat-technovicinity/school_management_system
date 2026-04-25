from django.contrib import admin
from .models import StudentAdmission, Parent, Contact, AcademicBackground, AdditionalInfo

admin.site.register(StudentAdmission)
admin.site.register(Parent)
admin.site.register(Contact)
admin.site.register(AcademicBackground)
admin.site.register(AdditionalInfo)

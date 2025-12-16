"""
URL configuration for school_management_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
# from django.urls import path

# urlpatterns = [
#     path('admin/', admin.site.urls),
# ]

from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="School Management System API",
        default_version="v1",
        description="API documentation for School Management System",
        terms_of_service="https://www.example.com/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,  # important
    permission_classes=(permissions.AllowAny,),  # no login required
)



urlpatterns = [
    # path("admin/", admin.site.urls),
    # your app APIs
    path("blog/", include("blog.urls")),

    ######### Mehedi##########
    path("auth/", include("userauthentication.urls")),

    #####addmission
    path("stdadmission/", include("student_admission.urls")),
    path("admissionexam/", include("admission_exam.urls")),

    ## Academic Management
    path("academic_class_routine/", include("academic_class_routine.urls")),
    path("academic_online_class/", include("academic_online_class.urls")),

    ### Student Management
    path("student_profile_create_all/", include("student_profile.urls")),



    ######## Exam Management
    path("exam_management_exam_setup/", include("exam_mm_exam_setup.urls")),
    path("exam_mm_exmroutine_exmadmit/", include("exam_mm_exmroutine_exmadmit.urls")),
    path("exam_mm_question_bank/", include("exam_mm_question_bank.urls")),
    path("exam_mm_result_archive/", include("exam_mm_result_archive.urls")),


    ######## account Management
    path("account_mm_stipend_student/", include('account_mm_std_stipent.urls')),
    path("account_mm_income/", include('account_mm_income.urls')),
    path("account_mm_voucher_generate/", include('account_mm_voucher_generate.urls')),
    path("account_mm_create_fee/", include('account_mm_create_fee.urls')),


    ##### Teacher Management
    path("teacher_mmss_workdistribute/", include('teacher_mm_workdistribute.urls')),
    path("teacher_mmm_comitee/", include('teacher_mm_comitee.urls')),
    path("teacher_mmm_teacher/", include('teacher_mm_teacher.urls')),
    path("teacher_mmm_teacher_leave/", include('teacher_mm_teacher_leave.urls')),




    ##### institute info Management
    path("institute_mm_institute_profile/", include('institute_mm_institute_profile.urls')),


    # Swagger
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]

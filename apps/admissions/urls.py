from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.admissions.views.admission_form import AdmissionFormViewSet
from apps.admissions.views.student_admission_views import stident_info_createapiview, student_info_get

router = DefaultRouter()
router.register(r'forms', AdmissionFormViewSet, basename='admission-forms')

urlpatterns = [
    # Router for the new Architecture API (/api/admissions/forms/)
    path('', include(router.urls)),
    
    # Old/Legacy API endpoints brought in from the merge
    path('register_student_info/', stident_info_createapiview.as_view(), name='register'),
    path('student_info/', student_info_get.as_view(), name='studentinfo'),
]
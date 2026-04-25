from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.admissions.views.admission_form import AdmissionFormViewSet
from apps.admissions.views.student_admission_views import stident_info_createapiview, student_info_get

from apps.admissions.views.bulk_admission import BulkImportAPIView
from apps.admissions.views.lottery_exam import LotteryExamViewSet
from apps.admissions.views.completion import AdmissionCompletionViewSet

router = DefaultRouter()
router.register(r'forms', AdmissionFormViewSet, basename='admission-forms')
router.register(r'lottery', LotteryExamViewSet, basename='admission-lottery')
router.register(r'completion', AdmissionCompletionViewSet, basename='admission-completion')

urlpatterns = [
    # Router for the new Architecture API (/api/admissions/...)
    path('', include(router.urls)),
    
    # Bulk Custom API
    path('bulk-import/', BulkImportAPIView.as_view(), name='admission-bulk-import'),
    
    # Old/Legacy API endpoints brought in from the merge
    path('register_student_info/', stident_info_createapiview.as_view(), name='register'),
    path('student_info/', student_info_get.as_view(), name='studentinfo'),
]
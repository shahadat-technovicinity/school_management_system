from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.admissions.views.admission_form import AdmissionFormViewSet

router = DefaultRouter()
router.register(r'forms', AdmissionFormViewSet, basename='admission-forms')

urlpatterns = [
    path('', include(router.urls)),
]
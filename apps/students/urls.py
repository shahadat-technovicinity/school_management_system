from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.student_management import StudentManagementViewSet
from .views.student_profile import StudentProfileViewSet

router = DefaultRouter()
router.register(r'management', StudentManagementViewSet, basename='student-management')
router.register(r'profile', StudentProfileViewSet, basename='student-profile')

urlpatterns = [
    path('', include(router.urls)),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.student_management import StudentManagementViewSet

router = DefaultRouter()
router.register(r'management', StudentManagementViewSet, basename='student-management')

urlpatterns = [
    path('', include(router.urls)),
]

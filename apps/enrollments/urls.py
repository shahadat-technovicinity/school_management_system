
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.enrollments.views.enrollments import EnrollmentViewSet

router = DefaultRouter()
router.register("enrollments", EnrollmentViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
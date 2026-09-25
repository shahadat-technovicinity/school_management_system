from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    LeaveTypeViewSet,
    TeacherLeaveViewSet,
    LeaveBalanceViewSet,
)

router = DefaultRouter()
router.register(r"leave-types", LeaveTypeViewSet, basename="leave-types")
router.register(r"leaves", TeacherLeaveViewSet, basename="teacher-leaves")
router.register(r"leave-balances", LeaveBalanceViewSet, basename="leave-balances")

urlpatterns = [
    path("", include(router.urls)),
]
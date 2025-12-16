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
    # All endpoints under /teacher/...
    # /teacher/leave-types/
    # /teacher/leaves/
    # /teacher/leave-balances/
    path("", include(router.urls)),
]

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.staff_views import (
    StaffProfileViewSet, 
    LeaveApplicationViewSet, 
    WorkAssignmentViewSet, 
    CommitteeViewSet
)

router = DefaultRouter()
router.register(r'profiles', StaffProfileViewSet, basename='staff-profile')
router.register(r'leaves', LeaveApplicationViewSet, basename='staff-leave')
router.register(r'work', WorkAssignmentViewSet, basename='staff-work')
router.register(r'committees', CommitteeViewSet, basename='staff-committee')

urlpatterns = [
    path('', include(router.urls)),
]

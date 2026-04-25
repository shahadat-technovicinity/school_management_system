from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.profile_views import StaffProfileViewSet
from .views.leave_views import LeaveApplicationViewSet
from .views.committee_views import (
    CommitteeViewSet, 
    CommitteeNoticeViewSet, 
    CommitteeCommunicationViewSet
)
from .views.work_views import WorkAssignmentViewSet

router = DefaultRouter()
router.register(r'profiles', StaffProfileViewSet, basename='staff-profile')
router.register(r'leaves', LeaveApplicationViewSet, basename='staff-leave')
router.register(r'committees', CommitteeViewSet, basename='staff-committee')
router.register(r'committee-notices', CommitteeNoticeViewSet, basename='committee-notice')
router.register(r'committee-communications', CommitteeCommunicationViewSet, basename='committee-communication')
router.register(r'work', WorkAssignmentViewSet, basename='staff-work')

urlpatterns = [
    path('', include(router.urls)),
]


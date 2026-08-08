from django.urls import path
from apps.attendance.views.attendance import AttendancePatchByKeyAPIView, BulkAttendanceAPIView, StudentAttendanceListAPIView


urlpatterns = [
    path("bulk/", BulkAttendanceAPIView.as_view()),
    path(
        'patch/',
        AttendancePatchByKeyAPIView.as_view(),
        name='attendance-patch-by-key'
    ),
    path(
        '',
        StudentAttendanceListAPIView.as_view(),
        name='attendance-list'
    ),
]

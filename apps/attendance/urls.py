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
        'student/<int:student_id>/',
        StudentAttendanceListAPIView.as_view(),
        name='student-attendance-list'
    ),
]

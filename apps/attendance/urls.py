from django.urls import path
from apps.attendance.views.attendance import BulkAttendanceAPIView


urlpatterns = [
    path("bulk/", BulkAttendanceAPIView.as_view()),
]

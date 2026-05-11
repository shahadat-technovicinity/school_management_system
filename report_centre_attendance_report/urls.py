from django.urls import path
from .views import AttendanceReportView

urlpatterns = [
    path('reports/attendance/', AttendanceReportView.as_view(), name='attendance-report'),
]
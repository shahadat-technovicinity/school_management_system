from django.urls import path
from .views import AccountStatsView, StudentAttendanceStatsView

urlpatterns = [
    path('stats/', AccountStatsView.as_view(), name='account-stats'),
    path('student-attendance-stats/', StudentAttendanceStatsView.as_view(), name='student-attendance-stats'),
]
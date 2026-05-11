from django.urls import path
from .views import StudentAgeDistributionReportView

urlpatterns = [
    path('reports/student-age-distribution/', StudentAgeDistributionReportView.as_view(), name='student-age-distribution'),
]
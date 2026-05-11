from django.urls import path
from .views import CrimeReportListCreateView, CrimeReportDetailView

urlpatterns = [
    path('crime-reports/', CrimeReportListCreateView.as_view(), name='crime-report-list'),
    path('crime-reports/<int:pk>/', CrimeReportDetailView.as_view(), name='crime-report-detail'),
]
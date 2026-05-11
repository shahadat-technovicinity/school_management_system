from django.urls import path
from .views import VisitingReportListCreateView, VisitingReportDetailView

urlpatterns = [
    path('visiting-reports/', VisitingReportListCreateView.as_view(), name='visiting-report-list'),
    path('visiting-reports/<int:pk>/', VisitingReportDetailView.as_view(), name='visiting-report-detail'),
]
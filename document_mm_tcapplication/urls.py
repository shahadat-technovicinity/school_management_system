from django.urls import path
from .views import (
    TCApplicationListCreateView,
    TCApplicationDetailView,
    TCApplicationStatusUpdateView,
    DownloadTCPDFView,
    MoveTCToNothiArchiveView,
)

urlpatterns = [
    path('applications/', TCApplicationListCreateView.as_view(), name='tc_application_list_create'),
    path('applications/<int:pk>/', TCApplicationDetailView.as_view(), name='tc_application_detail'),
    path('applications/<int:pk>/status/', TCApplicationStatusUpdateView.as_view(), name='tc_status_update'),
    path('applications/<int:pk>/download-pdf/', DownloadTCPDFView.as_view(), name='tc_download_pdf'),
    path('applications/<int:pk>/archive-to-nothi/', MoveTCToNothiArchiveView.as_view(), name='tc_archive_to_nothi'),
]
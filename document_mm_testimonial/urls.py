from django.urls import path
from .views import (
    StudentApplicationListCreateView,
    StudentApplicationDetailView,
    StudentApplicationStatusUpdateView,
    DownloadTestimonialPDFView,
    MoveToNothiArchiveView,
    VerifyTestimonialView,
)

urlpatterns = [
    path('applications/', StudentApplicationListCreateView.as_view(), name='application-list-create'),
    path('applications/<int:pk>/', StudentApplicationDetailView.as_view(), name='application-detail'),
    path('applications/<int:pk>/status/', StudentApplicationStatusUpdateView.as_view(), name='application-status-update'),
    path('applications/<int:pk>/download-pdf/', DownloadTestimonialPDFView.as_view(), name='application-download-pdf'),
    path('applications/<int:pk>/archive-to-nothi/', MoveToNothiArchiveView.as_view(), name='archive-to-nothi'),
    path('applications/<int:pk>/verify/', VerifyTestimonialView.as_view(), name='verify-testimonial'),
]
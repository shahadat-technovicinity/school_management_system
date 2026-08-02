from django.urls import path
from .views import (
    StudentFilterView,
    MarksListCreateAPIView,
    MarkRetrieveUpdateDestroyAPIView,
    AdminApprovedMarksListAPIView,
    AdminRejectedMarksListAPIView,
    AdminMarkStatusUpdateAPIView,
    FinalResultView
)

urlpatterns = [
    # General / Teacher Endpoints
    path('students/filter/', StudentFilterView.as_view(), name='student-filter'),
    path('marks/', MarksListCreateAPIView.as_view(), name='marks-list-create'), # GET-এ শুধু pending দেখাবে
    path('marks/<int:pk>/', MarkRetrieveUpdateDestroyAPIView.as_view(), name='marks-detail'),
    
    # Admin Approved / Rejected List Endpoints
    path('admin/marks/approved/', AdminApprovedMarksListAPIView.as_view(), name='admin-approved-marks'),
    path('admin/marks/rejected/', AdminRejectedMarksListAPIView.as_view(), name='admin-rejected-marks'),
    
    # Admin Status Change Endpoint (PATCH)
    path('admin/marks/<int:pk>/status/', AdminMarkStatusUpdateAPIView.as_view(), name='admin-change-mark-status'),
    
    # Result Sheet
    path('final-results/', FinalResultView.as_view(), name='final-results'),
]
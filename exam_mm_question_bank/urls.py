from django.urls import path
from .views import (
    QuestionListCreateAPIView,
    QuestionDetailAPIView,
    AdminApprovedQuestionListAPIView,
    AdminRejectedQuestionListAPIView,
    AdminQuestionStatusUpdateAPIView,
)

urlpatterns = [
    # Main Questions Endpoint (Get all / Create)
    path('questions/', QuestionListCreateAPIView.as_view(), name='question-list-create'),
    path('questions/<int:pk>/', QuestionDetailAPIView.as_view(), name='question-detail-delete'),
    
    # Admin Approved & Rejected Endpoints
    path('admin/questions/approved/', AdminApprovedQuestionListAPIView.as_view(), name='admin-approved-questions'),
    path('admin/questions/rejected/', AdminRejectedQuestionListAPIView.as_view(), name='admin-rejected-questions'),
    
    # Admin Status Change Endpoint
    path('admin/questions/<int:pk>/status/', AdminQuestionStatusUpdateAPIView.as_view(), name='admin-change-status'),
]
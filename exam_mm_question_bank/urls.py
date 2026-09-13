from django.urls import path
from .views import (
    QuestionBankListCreateView,
    QuestionBankDetailView,
    QuestionBankStatusUpdateView
)

urlpatterns = [
    # List all questions or Upload a new question
    path('question-bank/', QuestionBankListCreateView.as_view(), name='question-bank-list-create'),
    
    # Retrieve, Update, or Delete a specific question
    path('question-bank/<int:pk>/', QuestionBankDetailView.as_view(), name='question-bank-detail'),
    
    # Approve or Reject a question status
    path('question-bank/<int:pk>/status/', QuestionBankStatusUpdateView.as_view(), name='question-bank-status-update'),
]
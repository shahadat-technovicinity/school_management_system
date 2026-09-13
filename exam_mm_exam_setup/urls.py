from django.urls import path
from .views import (
    ExamNameListCreateView, 
    ExamNameDetailView, 
    ExamSetupListCreateView, 
    ExamSetupDetailView
)

urlpatterns = [
    # Exam Name Endpoints
    path('exam-names/', ExamNameListCreateView.as_view(), name='exam-name-list-create'),
    path('exam-names/<int:pk>/', ExamNameDetailView.as_view(), name='exam-name-detail'),
    
    # Exam Setup/Configuration Endpoints
    path('exam-setups/', ExamSetupListCreateView.as_view(), name='exam-setup-list-create'),
    path('exam-setups/<int:pk>/', ExamSetupDetailView.as_view(), name='exam-setup-detail'),
]
from django.urls import path
from .views import (
    ExamDutyListCreateView, 
    ExamDutyDetailView, 
    ExamDutyStatusUpdateView
)

urlpatterns = [
    path('exam-duties/', ExamDutyListCreateView.as_view(), name='exam-duty-list-create'),
    path('exam-duties/<int:pk>/', ExamDutyDetailView.as_view(), name='exam-duty-detail'),
    path('exam-duties/<int:pk>/status/', ExamDutyStatusUpdateView.as_view(), name='exam-duty-status-update'),
]
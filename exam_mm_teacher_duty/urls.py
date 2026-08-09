from django.urls import path
from .views import (
    ExamDutyListCreateView, ExamDutyDetailView,
    ExamDutyStatusUpdateView, ArchivedExamDutyListView, DutyStatsView
)

urlpatterns = [
    path('duties/', ExamDutyListCreateView.as_view(), name='exam-duty-list'),
    path('duties/<int:pk>/', ExamDutyDetailView.as_view(), name='exam-duty-detail'),
    path('duties/<int:pk>/status/', ExamDutyStatusUpdateView.as_view(), name='exam-duty-status'),
    path('duties/archive/', ArchivedExamDutyListView.as_view(), name='exam-duty-archive'),
    path('duties/stats/', DutyStatsView.as_view(), name='exam-duty-stats'),
]


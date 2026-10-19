from django.urls import path
from .views import (
    ExamResultConfigListCreateView,
    ExamResultConfigDetailView,
    StudentDetailedMarksheetView,
    StudentListByClassSectionView,
    StudentExamResultListCreateView,
    StudentExamResultDetailView,
    BulkResultInputView,
)

urlpatterns = [
    path('result-config/', ExamResultConfigListCreateView.as_view(), name='result-config-list'),
    path('result-config/<int:pk>/', ExamResultConfigDetailView.as_view(), name='result-config-detail'),
    path('students/', StudentListByClassSectionView.as_view(), name='student-list-for-result'),
    path('results/', StudentExamResultListCreateView.as_view(), name='result-list'),
    path('results/<int:pk>/', StudentExamResultDetailView.as_view(), name='result-detail'),
    path('results/bulk/', BulkResultInputView.as_view(), name='bulk-result-input'),
    path('student-marksheet/<int:student_id>/', StudentDetailedMarksheetView.as_view(), name='student-detailed-marksheet'),
]
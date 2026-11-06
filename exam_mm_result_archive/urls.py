from django.urls import path
from .views import (
    ClassSectionResultSummaryView,
    ExamResultConfigListCreateView,
    ExamResultConfigDetailView,
    StudentDetailedMarksheetView,
    StudentListByClassSectionView,
    StudentExamResultListCreateView,
    StudentExamResultDetailView,
    BulkResultInputView,
)
from .combined import (
    CombinedResultConfigListCreateView,
    CombinedResultConfigDetailView,
    CombinedResultView,
)

urlpatterns = [
    path('result-config/', ExamResultConfigListCreateView.as_view(), name='result-config-list'),
    path('result-config/<int:pk>/', ExamResultConfigDetailView.as_view(), name='result-config-detail'),
    path('students/', StudentListByClassSectionView.as_view(), name='student-list-for-result'),
    path('results/', StudentExamResultListCreateView.as_view(), name='result-list'),
    path('results/<int:pk>/', StudentExamResultDetailView.as_view(), name='result-detail'),
    path('results/bulk/', BulkResultInputView.as_view(), name='bulk-result-input'),
    path('student-marksheet/<int:student_id>/', StudentDetailedMarksheetView.as_view(), name='student-detailed-marksheet'),
    path('class-section-result-summary/', ClassSectionResultSummaryView.as_view(), name='class-section-result-summary'),


    # Combined Result URLs
    path('combined-result-config/', CombinedResultConfigListCreateView.as_view(), name='combined-result-config-list'),
    path('combined-result-config/<int:pk>/', CombinedResultConfigDetailView.as_view(), name='combined-result-config-detail'),
    path('combined-results/', CombinedResultView.as_view(), name='combined-results'),

]
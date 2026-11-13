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
    RecalculateResultsView,
    GraceMarksApplyView,
    SubjectGroupListCreateView,
    SubjectGroupDetailView,
    GradeScaleListCreateView,
    GradeScaleDetailView,
    Class68ResultConfigListCreateView,
    Class68ResultConfigDetailView,
    Class68StudentListView,
    Class68BulkResultInputView,
    Class68StudentMarksheetView,
    Class68ResultSummaryView,
    Class910ResultConfigListCreateView,
    Class910ResultConfigDetailView,
    Class910StudentListView,
    Class910BulkResultInputView,
    Class910StudentMarksheetView,
    Class910ResultSummaryView,
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
    path('results/recalculate/', RecalculateResultsView.as_view(), name='result-recalculate'),
    path('grace-marks/apply/', GraceMarksApplyView.as_view(), name='grace-marks-apply'),
    path('student-marksheet/<int:student_id>/', StudentDetailedMarksheetView.as_view(), name='student-detailed-marksheet'),
    path('class-section-result-summary/', ClassSectionResultSummaryView.as_view(), name='class-section-result-summary'),

    # Admin: বিষয় গ্রুপ (English = 1st + 2nd paper) ও Grade তালিকা
    path('subject-groups/', SubjectGroupListCreateView.as_view(), name='subject-group-list'),
    path('subject-groups/<int:pk>/', SubjectGroupDetailView.as_view(), name='subject-group-detail'),
    path('grade-scales/', GradeScaleListCreateView.as_view(), name='grade-scale-list'),
    path('grade-scales/<int:pk>/', GradeScaleDetailView.as_view(), name='grade-scale-detail'),

    # ক্লাস ৬-৮ এর আলাদা API (written + mcq)
    path('class-6-8/result-config/', Class68ResultConfigListCreateView.as_view(), name='c68-result-config-list'),
    path('class-6-8/result-config/<int:pk>/', Class68ResultConfigDetailView.as_view(), name='c68-result-config-detail'),
    path('class-6-8/students/', Class68StudentListView.as_view(), name='c68-students'),
    path('class-6-8/results/bulk/', Class68BulkResultInputView.as_view(), name='c68-bulk-result-input'),
    path('class-6-8/student-marksheet/<int:student_id>/', Class68StudentMarksheetView.as_view(), name='c68-student-marksheet'),
    path('class-6-8/class-section-result-summary/', Class68ResultSummaryView.as_view(), name='c68-result-summary'),

    # ক্লাস ৯-১০ এর আলাদা API (written + mcq + practical)
    path('class-9-10/result-config/', Class910ResultConfigListCreateView.as_view(), name='c910-result-config-list'),
    path('class-9-10/result-config/<int:pk>/', Class910ResultConfigDetailView.as_view(), name='c910-result-config-detail'),
    path('class-9-10/students/', Class910StudentListView.as_view(), name='c910-students'),
    path('class-9-10/results/bulk/', Class910BulkResultInputView.as_view(), name='c910-bulk-result-input'),
    path('class-9-10/student-marksheet/<int:student_id>/', Class910StudentMarksheetView.as_view(), name='c910-student-marksheet'),
    path('class-9-10/class-section-result-summary/', Class910ResultSummaryView.as_view(), name='c910-result-summary'),

    # Combined Result URLs
    path('combined-result-config/', CombinedResultConfigListCreateView.as_view(), name='combined-result-config-list'),
    path('combined-result-config/<int:pk>/', CombinedResultConfigDetailView.as_view(), name='combined-result-config-detail'),
    path('combined-results/<int:config_id>/', CombinedResultView.as_view(), name='combined-results'),
]
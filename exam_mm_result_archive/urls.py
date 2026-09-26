from django.urls import path
from .views import (
    StudentFilterView,
    MarksListCreateAPIView,
    MarkRetrieveUpdateDestroyAPIView,
    AdminApprovedMarksListAPIView,
    AdminRejectedMarksListAPIView,
    AdminMarkStatusUpdateAPIView,
    FinalResultView,
    SubjectPassMarkConfigListCreateAPIView,
    SubjectPassMarkConfigDetailAPIView,
    GradeScaleListCreateAPIView,
    GradeScaleDetailAPIView,
)

urlpatterns = [
    # Teacher Student Filter
    path('students/filter/', StudentFilterView.as_view(), name='students_filter_list'),

    # Teacher Marks Entry & List
    path('marks/', MarksListCreateAPIView.as_view(), name='marks_list_create'),
    path('marks/<int:pk>/', MarkRetrieveUpdateDestroyAPIView.as_view(), name='marks_detail_update'),

    # Admin Marks Review & Status Update
    path('admin/marks/approved/', AdminApprovedMarksListAPIView.as_view(), name='admin_marks_approved_list'),
    path('admin/marks/rejected/', AdminRejectedMarksListAPIView.as_view(), name='admin_marks_rejected_list'),
    path('admin/marks/<int:pk>/status/', AdminMarkStatusUpdateAPIView.as_view(), name='admin_marks_status_partial_update'),

    # Admin Config Setup
    path('admin/config/pass-marks/', SubjectPassMarkConfigListCreateAPIView.as_view(), name='admin_pass_marks_config_list'),
    path('admin/config/pass-marks/<int:pk>/', SubjectPassMarkConfigDetailAPIView.as_view(), name='admin_pass_marks_config_detail'),
    path('admin/config/grade-scale/', GradeScaleListCreateAPIView.as_view(), name='admin_grade_scale_config_list'),
    path('admin/config/grade-scale/<int:pk>/', GradeScaleDetailAPIView.as_view(), name='admin_grade_scale_config_detail'),

    # Final Result & Merit List
    path('final-results/', FinalResultView.as_view(), name='final_results_list'),
]
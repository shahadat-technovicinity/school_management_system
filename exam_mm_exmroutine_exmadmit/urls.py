from django.urls import path
from .views import (
    ExamRoutineListCreateView,
    ExamRoutineDetailView,
    ClassWiseAdmitCardGenerateView
)

urlpatterns = [
    # Routine management routes
    path('exam-routines/', ExamRoutineListCreateView.as_view(), name='exam-routine-list-create'),
    path('exam-routines/<int:pk>/', ExamRoutineDetailView.as_view(), name='exam-routine-detail'),
    
    # Admit card generation endpoint (supports exam_id, class_id, section_id, and student_id query params)
    path('exam-routines/admit-cards/', ClassWiseAdmitCardGenerateView.as_view(), name='generate-admit-cards'),
]
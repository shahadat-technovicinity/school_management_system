from django.urls import path
from .views import (
    ExamRoutineListCreateView,
    ExamRoutineDetailView,
    ClassWiseAdmitCardGenerateView,
    AdmitCardPrintView,
)

urlpatterns = [
    # Routine management routes
    path('exam-routines/', ExamRoutineListCreateView.as_view(), name='exam-routine-list-create'),
    path('exam-routines/<int:pk>/', ExamRoutineDetailView.as_view(), name='exam-routine-detail'),
    
    # Admit card generation endpoint (supports exam_id, class_id, section_id, and student_id query params)
    path('exam-routines/admit-cards/', ClassWiseAdmitCardGenerateView.as_view(), name='generate-admit-cards'),
    path('exam-routines/admit-cards/<int:student_id>/', ClassWiseAdmitCardGenerateView.as_view(), name='generate-admit-card-for-student'),
    path('exam-routines/admit-cards/print/<int:student_id>/', AdmitCardPrintView.as_view(), name='print-admit-card'),
]
from django.urls import path
from .views import (
    ExamAttendanceSheetPrintView,
    ExamRoutineListCreateView,
    ExamRoutineDetailView,
    ClassWiseAdmitCardGenerateView,
    AdmitCardPrintView,
)

urlpatterns = [
    path('exam-routines/', ExamRoutineListCreateView.as_view(), name='exam-routine-list-create'),
    path('exam-routines/<int:pk>/', ExamRoutineDetailView.as_view(), name='exam-routine-detail'),

    path('exam-routines/admit-cards/', ClassWiseAdmitCardGenerateView.as_view(), name='generate-admit-cards'),
    path('exam-routines/admit-cards/<int:student_id>/', ClassWiseAdmitCardGenerateView.as_view(), name='generate-admit-card-for-student'),

    # একজনের admit card (PDF)
    path('exam-routines/admit-cards/print/<int:student_id>/', AdmitCardPrintView.as_view(), name='print-admit-card'),
    # ক্লাস/সেকশন/পরীক্ষা দিয়ে সবার admit card (PDF)
    path('exam-routines/admit-cards/print/', AdmitCardPrintView.as_view(), name='print-admit-cards'),

    # পরীক্ষার উপর ভিত্তি করে attendance sheet (PDF)
    path('exam-routines/attendance-sheets/print/', ExamAttendanceSheetPrintView.as_view(), name='print-attendance-sheets'),
]
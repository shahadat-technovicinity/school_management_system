from django.urls import path, include
from .views import *


urlpatterns = [
    path("exam_routine", ExamRoutineListCreateView.as_view(), name='exam_routine'),
    path("exam_routine_action/<int:pk>/", ExamRoutineDetailView.as_view(), name = 'exam_r_action'),

    ######  admit header   ##########

    path("exam_admit", ExamAdmitListCreateView.as_view(), name='exam_routine'),
    path("exam_admit_action/<int:pk>/", ExamAdmitDetailView.as_view(), name = 'exam_r_action'),


    ######   admit generate summary dashboard api endpoin ########
    path("admit_card_generate_summary_dashboard/", AdmitCardSummaryDashboardAPIView.as_view(), name = 'admitgeneratesummarydashboard'),

]
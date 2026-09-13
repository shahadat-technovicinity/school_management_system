from django.urls import path
from .views import ExamRoutineListCreateView, ExamRoutineDetailView

urlpatterns = [
    path("exam-routines/", ExamRoutineListCreateView.as_view(), name='exam-routine-list-create'),
    path("exam-routines/<int:pk>/", ExamRoutineDetailView.as_view(), name='exam-routine-detail'),
]
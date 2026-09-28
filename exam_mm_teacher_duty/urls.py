from django.urls import path
from .views import (
    ExamDutyListCreateView,
    TeacherMyExamDutyListView,
    ExamDutyDetailView,
    ExamDutyStatusUpdateView
)

urlpatterns = [
    # অ্যাডমিন সব দেখতে ও তৈরি করতে পারবে + সাধারণ টিচাররা শুধু নিজেরটা দেখতে পাবে
    path('exam-duties/', ExamDutyListCreateView.as_view(), name='exam_duty_list_create'),
    
    # টিচার নিজের জন্য আলাদা নিবেদিত Endpoint (Frontend-এ My Duties Tab-এর জন্য সুবিধাজনক)
    path('exam-duties/my-duties/', TeacherMyExamDutyListView.as_view(), name='my_exam_duties'),
    
    path('exam-duties/<int:pk>/', ExamDutyDetailView.as_view(), name='exam_duty_detail'),
    path('exam-duties/<int:pk>/status/', ExamDutyStatusUpdateView.as_view(), name='exam_duty_status_update'),
]
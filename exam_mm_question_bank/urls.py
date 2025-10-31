from django.urls import path
from . import views

urlpatterns = [
    path('questions/', views.QuestionListCreateAPIView.as_view(), name='question-list-create'),
    path('questions/<int:pk>/', views.QuestionRetrieveAPIView.as_view(), name='question-retrieve'), 
    path('admin/pending/', views.AdminPendingQuestionListAPIView.as_view(), name='admin-pending-list'),
    path('admin/status/<int:pk>/', views.admin_change_status, name='admin-change-status'),
]
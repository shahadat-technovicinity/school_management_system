from django.urls import path
from .views import *

urlpatterns = [
    path('students/', Top_StudentListCreateView.as_view(), name='student-list-create'),
    path('students/<int:pk>/', Top_StudentDetailView.as_view(), name='student-detail'),
]
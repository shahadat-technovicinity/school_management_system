from django.urls import path
from .views import *

urlpatterns = [
    path('students/', StudentTopListCreateView.as_view(), name='student-top-list-create'),
    path('students/<int:pk>/', StudentTopDetailView.as_view(), name='student-top-detail'),
]
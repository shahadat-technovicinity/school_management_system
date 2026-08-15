from django.urls import path
from .views import (
    StudentApplicationListCreateView,
    StudentApplicationDetailView,
    StudentApplicationStatusUpdateView,
)

urlpatterns = [
    path('applications/', StudentApplicationListCreateView.as_view(), name='application-list-create'),
    path('applications/<int:pk>/', StudentApplicationDetailView.as_view(), name='application-detail'),
    path('applications/<int:pk>/status/', StudentApplicationStatusUpdateView.as_view(), name='application-status-update'),
]
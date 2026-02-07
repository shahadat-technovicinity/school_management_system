from django.urls import path
from .views import TrainingListCreateView, TrainingDetailView

urlpatterns = [
    # Training table list ebong form save korar endpoint
    path('trainings/', TrainingListCreateView.as_view(), name='training-list-create'),
    
    # Specific record edit/delete endpoint
    path('trainings/<int:pk>/', TrainingDetailView.as_view(), name='training-detail'),
]
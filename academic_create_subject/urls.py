from django.urls import path
from .views import SubjectListCreateView, SubjectRetrieveUpdateDestroyView

urlpatterns = [
    path('subjects/', SubjectListCreateView.as_view(), name='subject-list-create'),
    path('subjects/<int:pk>/', SubjectRetrieveUpdateDestroyView.as_view(), name='subject-detail'),
]
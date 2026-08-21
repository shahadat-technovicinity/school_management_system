from django.urls import path
from .views import (
    AcademicClassListCreateView,
    AcademicClassDetailView,
    SectionListCreateView,
    SectionDetailView
)

urlpatterns = [
    # Class Endpoints
    path('classes/', AcademicClassListCreateView.as_view(), name='class-list-create'),
    path('classes/<int:pk>/', AcademicClassDetailView.as_view(), name='class-detail'),

    # Independent Section Endpoints
    path('sections/', SectionListCreateView.as_view(), name='section-list-create'),
    path('sections/<int:pk>/', SectionDetailView.as_view(), name='section-detail'),
]
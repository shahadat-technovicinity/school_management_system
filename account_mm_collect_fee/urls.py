from django.urls import path
from .views import (
    StudentFeeSearchView,
    FeeCollectionListCreateView,
    FeeCollectionDetailView,
)

urlpatterns = [
    path('fees/search/', StudentFeeSearchView.as_view(), name='student-fee-search'),
    path('fees/collect/', FeeCollectionListCreateView.as_view(), name='fee-collection-list'),
    path('fees/collect/<int:pk>/', FeeCollectionDetailView.as_view(), name='fee-collection-detail'),
]
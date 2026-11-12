from django.urls import path

from .views import FeeHeadDetailView, FeeHeadListCreateView, FeeHeadTreeView

urlpatterns = [
    path('fee-heads/', FeeHeadListCreateView.as_view(), name='fee-head-list'),
    path('fee-heads/tree/', FeeHeadTreeView.as_view(), name='fee-head-tree'),
    path('fee-heads/<int:pk>/', FeeHeadDetailView.as_view(), name='fee-head-detail'),
]
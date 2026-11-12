from django.urls import path

from .views import (
    FeeFormItemsView,
    FeeStructureDetailView,
    FeeStructureListCreateView,
    StudentPickerView,
)

urlpatterns = [
    path('fee-structures/', FeeStructureListCreateView.as_view(), name='fee-structure-list'),
    path('fee-structures/form-items/', FeeFormItemsView.as_view(), name='fee-structure-form-items'),
    path('fee-structures/students/', StudentPickerView.as_view(), name='fee-structure-students'),
    path('fee-structures/<int:pk>/', FeeStructureDetailView.as_view(), name='fee-structure-detail'),
]
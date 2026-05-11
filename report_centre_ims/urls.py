from django.urls import path
from .views import SystemOverviewView, SystemActivityView, UserManagementView, InventoryManagementView

urlpatterns = [
    path('ims/system-overview/', SystemOverviewView.as_view(), name='system-overview'),
    path('ims/activity/', SystemActivityView.as_view(), name='system-activity'),
    path('ims/user-management/', UserManagementView.as_view(), name='user-management'),
    path('ims/inventory/', InventoryManagementView.as_view(), name='inventory-management'),
]
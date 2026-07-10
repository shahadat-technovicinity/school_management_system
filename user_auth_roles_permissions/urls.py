from django.urls import path
from .views import *

urlpatterns = [
    # Role
    path('roles/', RoleListCreateView.as_view(), name='role-list-create'),
    path('roles/<int:pk>/', RoleRetrieveUpdateDestroyView.as_view(), name='role-detail'),

    # Feature
    path('features/', FeatureListView.as_view(), name='feature-list'),

    # Role এর সব Feature permission একসাথে দেখাও
    path('roles/<int:role_id>/permissions/', RolePermissionAllView.as_view(), name='role-permissions-all'),

    # Bulk update
    path('roles/<int:role_id>/permissions/bulk-update/', RolePermissionBulkUpdateView.as_view(), name='role-permissions-bulk-update'),
]
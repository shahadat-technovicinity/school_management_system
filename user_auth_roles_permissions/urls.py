from django.urls import path
from .views import *

urlpatterns = [
    # Role
    path('roles/', RoleListCreateView.as_view(), name='role-list-create'),
    path('roles/<int:pk>/', RoleRetrieveUpdateDestroyView.as_view(), name='role-detail'),

    # Permission
    path('permissions/', PermissionListCreateView.as_view(), name='permission-list-create'),
    path('permissions/<int:pk>/', PermissionRetrieveUpdateDestroyView.as_view(), name='permission-detail'),

    # RolePermission (Role ↔ Permission M2M mapping)
    path('role-permissions/', RolePermissionListCreateView.as_view(), name='role-permission-list-create'),
    path('role-permissions/<int:pk>/', RolePermissionRetrieveUpdateDestroyView.as_view(), name='role-permission-detail'),
]

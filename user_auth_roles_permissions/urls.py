from django.urls import path
from .views import *

urlpatterns = [
    # Role
    path('roles/', RoleListCreateView.as_view(), name='role-list-create'),
    path('roles/<int:pk>/', RoleRetrieveUpdateDestroyView.as_view(), name='role-detail'),

    path('available-features/', AvailableFeaturesAPIView.as_view(), name='available-features'),
    
    path('assign-permissions/', AssignFeaturePermissionsAPIView.as_view(), name='assign-permissions'),
]

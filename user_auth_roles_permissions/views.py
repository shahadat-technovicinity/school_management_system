from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Role, Permission, RolePermission
from .serializers import RoleSerializer, PermissionSerializer, RolePermissionSerializer


# ── Role CRUD ─────────────────────────────────────────────────────────────────
class RoleListCreateView(generics.ListCreateAPIView):
    queryset = Role.objects.prefetch_related('role_permissions__permission').all()
    serializer_class = RoleSerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdminUser]


class RoleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Role.objects.prefetch_related('role_permissions__permission').all()
    serializer_class = RoleSerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdminUser]


# ── Permission CRUD ───────────────────────────────────────────────────────────
class PermissionListCreateView(generics.ListCreateAPIView):
   
    serializer_class = PermissionSerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = Permission.objects.all()
        group_name = self.request.query_params.get('group_name')
        if group_name:
            qs = qs.filter(group_name__iexact=group_name)
        return qs


class PermissionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdminUser]


# ── RolePermission CRUD ───────────────────────────────────────────────────────
class RolePermissionListCreateView(generics.ListCreateAPIView):
   
    serializer_class = RolePermissionSerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = RolePermission.objects.select_related('role', 'permission').all()
        role_id = self.request.query_params.get('role_id')
        if role_id:
            qs = qs.filter(role_id=role_id)
        return qs


class RolePermissionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    
    queryset = RolePermission.objects.select_related('role', 'permission').all()
    serializer_class = RolePermissionSerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdminUser]
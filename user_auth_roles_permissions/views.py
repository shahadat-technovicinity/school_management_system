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
    """
    GET  /permissions/               → সব feature list
                                       ?group_name=<name> দিয়ে ফিল্টার
    POST /permissions/               → নতুন feature তৈরি
    """
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
    """
    GET  /role-permissions/          → সব RolePermission list
                                       ?role_id=<pk> দিয়ে ফিল্টার
    POST /role-permissions/          → নতুন mapping তৈরি

    POST body example:
        {
            "role": 1,
            "permission": 3,
            "can_view": true,
            "can_create": false,
            "can_edit": false,
            "can_delete": false
        }
    """
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
    """
    GET    /role-permissions/<pk>/   → একটি mapping দেখুন
    PUT    /role-permissions/<pk>/   → সম্পূর্ণ আপডেট
    PATCH  /role-permissions/<pk>/   → আংশিক আপডেট (e.g. শুধু can_edit পরিবর্তন)
    DELETE /role-permissions/<pk>/   → mapping মুছে ফেলুন
    """
    queryset = RolePermission.objects.select_related('role', 'permission').all()
    serializer_class = RolePermissionSerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdminUser]
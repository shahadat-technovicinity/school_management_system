from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Role, Permission, RolePermission
from .serializers import (
    RoleSerializer,
    PermissionSerializer,
    RolePermissionSerializer,
)


# ── Role CRUD ─────────────────────────────────────────────────────────────────
class RoleListCreateView(generics.ListCreateAPIView):
    """
    GET  /roles/   → সব Role লিস্ট (nested role_permissions সহ)
    POST /roles/   → নতুন Role তৈরি
    """
    queryset = Role.objects.prefetch_related('role_permissions__permissions').all()
    serializer_class = RoleSerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdminUser]


class RoleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /roles/<pk>/   → একটি Role দেখুন
    PUT    /roles/<pk>/   → সম্পূর্ণ আপডেট
    PATCH  /roles/<pk>/   → আংশিক আপডেট
    DELETE /roles/<pk>/   → মুছে ফেলুন
    """
    queryset = Role.objects.prefetch_related('role_permissions__permissions').all()
    serializer_class = RoleSerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdminUser]


# ── Permission CRUD ───────────────────────────────────────────────────────────
class PermissionListCreateView(generics.ListCreateAPIView):
    """
    GET  /permissions/          → সব Permission লিস্ট।
                                  ?group_name=<name> দিয়ে ফিল্টার করা যাবে।
    POST /permissions/          → নতুন Permission তৈরি।
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
    """
    GET    /permissions/<pk>/   → একটি Permission দেখুন
    PUT    /permissions/<pk>/   → সম্পূর্ণ আপডেট
    PATCH  /permissions/<pk>/   → আংশিক আপডেট
    DELETE /permissions/<pk>/   → মুছে ফেলুন
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdminUser]


# ── RolePermission CRUD ───────────────────────────────────────────────────────
class RolePermissionListCreateView(generics.ListCreateAPIView):
    """
    GET  /role-permissions/          → সব RolePermission লিস্ট।
                                       ?role_id=<pk> দিয়ে ফিল্টার করা যাবে।
    POST /role-permissions/          → নতুন RolePermission তৈরি।

    POST body example:
        {
            "role": 1,
            "permission_ids": [2, 5, 7]
        }
    """
    serializer_class = RolePermissionSerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = RolePermission.objects.select_related('role').prefetch_related('permissions').all()
        role_id = self.request.query_params.get('role_id')
        if role_id:
            qs = qs.filter(role_id=role_id)
        return qs


class RolePermissionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /role-permissions/<pk>/   → একটি RolePermission দেখুন
    PUT    /role-permissions/<pk>/   → সম্পূর্ণ আপডেট
    PATCH  /role-permissions/<pk>/   → আংশিক আপডেট (permission_ids সহ)
    DELETE /role-permissions/<pk>/   → মুছে ফেলুন
    """
    queryset = RolePermission.objects.select_related('role').prefetch_related('permissions').all()
    serializer_class = RolePermissionSerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdminUser]
from rest_framework import serializers
from .models import Role, RolePermission

class RolePermissionGridSerializer(serializers.ModelSerializer):
    class Meta:
        model = RolePermission
        fields = ['feature_name', 'feature_slug', 'can_create', 'can_view', 'can_edit', 'can_delete']


class RoleSerializer(serializers.ModelSerializer):
    permissions = RolePermissionGridSerializer(source='feature_permissions', many=True, read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'name', 'permissions', 'created_at']
from rest_framework import serializers
from .models import Role, Permission, RolePermission


# ── Permission serializer (feature definition only) ───────────────────────────
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'group_name', 'feature_name', 'feature_slug']


# ── RolePermission serializer ─────────────────────────────────────────────────
class RolePermissionSerializer(serializers.ModelSerializer):
    """
    Read  → shows nested permission object + role name
    Write → send role PK + permission PK + CRUD flags
    """
    permission_detail = PermissionSerializer(source='permission', read_only=True)
    role_name = serializers.CharField(source='role.name', read_only=True)

    class Meta:
        model = RolePermission
        fields = [
            'id',
            'role',
            'role_name',
            'permission',
            'permission_detail',
            'can_create',
            'can_view',
            'can_edit',
            'can_delete',
        ]


# ── Role serializer (with all its feature permissions) ────────────────────────
class RoleSerializer(serializers.ModelSerializer):
    role_permissions = RolePermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'name', 'role_permissions', 'created_at']

# ── Role serializer (Dropdown) ────────────────────────────────────────────────
class RoleDropdownSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name']
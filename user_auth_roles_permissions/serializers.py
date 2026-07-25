from rest_framework import serializers
from .models import Role, Permission, RolePermission


# ── Permission CRUD serializer ────────────────────────────────────────────────
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = [
            'id',
            'group_name',
            'feature_name',
            'feature_slug',
            'can_create',
            'can_view',
            'can_edit',
            'can_delete',
        ]


# ── RolePermission serializers ────────────────────────────────────────────────
class RolePermissionSerializer(serializers.ModelSerializer):
    """
    Full CRUD serializer for RolePermission.
    - On read  : permissions field shows nested Permission objects.
    - On write : send a list of Permission PKs  e.g. {"role": 1, "permissions": [2, 5]}
    """
    role_name = serializers.CharField(source='role.name', read_only=True)
    permissions = PermissionSerializer(many=True, read_only=True)
    permission_ids = serializers.PrimaryKeyRelatedField(
        source='permissions',
        queryset=Permission.objects.all(),
        many=True,
        write_only=True,
        required=False,
    )

    class Meta:
        model = RolePermission
        fields = [
            'id',
            'role',
            'role_name',
            'permissions',       # read  → nested objects
            'permission_ids',    # write → list of PKs
        ]


# ── Role serializer ───────────────────────────────────────────────────────────
class RoleSerializer(serializers.ModelSerializer):
    """
    Shows a Role with all its RolePermission entries (each containing
    the nested Permission list).
    """
    role_permissions = RolePermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Role
        fields = ['id', 'name', 'role_permissions', 'created_at']
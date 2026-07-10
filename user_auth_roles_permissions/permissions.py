from rest_framework.permissions import BasePermission
from .models import RolePermission


class HasFeaturePermission(BasePermission):

    def has_permission(self, request, view):
        user = request.user

        if not user.is_authenticated:
            return False

        if user.is_superuser:
            return True

        feature_name = getattr(view, 'feature_name', None)
        if not feature_name:
            return False

        role = getattr(user, 'role', None)
        if not role:
            return False

        try:
            perm = RolePermission.objects.get(
                role__name=role,
                feature__name=feature_name
            )
        except RolePermission.DoesNotExist:
            return False

        method_map = {
            'GET':    perm.can_view,
            'POST':   perm.can_create,
            'PUT':    perm.can_edit,
            'PATCH':  perm.can_edit,
            'DELETE': perm.can_delete,
        }

        return method_map.get(request.method, False)
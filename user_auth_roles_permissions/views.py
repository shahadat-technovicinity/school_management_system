from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Role, Feature, RolePermission
from .serializers import (
    RoleSerializer, FeatureSerializer,
    RolePermissionSerializer, RoleFeaturePermissionSerializer,
    BulkPermissionSerializer
)


# Role CRUD
class RoleListCreateView(generics.ListCreateAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdminUser]


class RoleRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdminUser]


# Feature List
class FeatureListView(generics.ListAPIView):
    queryset = Feature.objects.all()
    serializer_class = FeatureSerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdminUser]


# একটা Role এর সব Feature permission একসাথে দেখাবে
class RolePermissionAllView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdminUser]

    def get(self, request, role_id):
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response({"error": "Role not found"}, status=status.HTTP_404_NOT_FOUND)

        # সব feature নাও
        all_features = Feature.objects.all()

        # এই role এর existing permissions
        existing_perms = RolePermission.objects.filter(role=role)
        perm_map = {p.feature_id: p for p in existing_perms}

        result = []
        for feature in all_features:
            perm = perm_map.get(feature.id)
            result.append({
                'feature_id': feature.id,
                'feature_name': feature.name,
                'display_name': feature.display_name,
                'can_view': perm.can_view if perm else False,
                'can_create': perm.can_create if perm else False,
                'can_edit': perm.can_edit if perm else False,
                'can_delete': perm.can_delete if perm else False,
            })

        serializer = RoleFeaturePermissionSerializer(result, many=True)
        return Response(serializer.data)


# Bulk update — Admin checkbox tick করে একসাথে save করবে
class RolePermissionBulkUpdateView(APIView):
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdminUser]

    def post(self, request, role_id):
        try:
            role = Role.objects.get(id=role_id)
        except Role.DoesNotExist:
            return Response({"error": "Role not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = BulkPermissionSerializer(data=request.data, many=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        for item in serializer.validated_data:
            feature = item['feature_id']
            RolePermission.objects.update_or_create(
                role=role,
                feature=feature,
                defaults={
                    'can_view': item['can_view'],
                    'can_create': item['can_create'],
                    'can_edit': item['can_edit'],
                    'can_delete': item['can_delete'],
                }
            )

        return Response({"message": "Permissions updated successfully"}, status=status.HTTP_200_OK)
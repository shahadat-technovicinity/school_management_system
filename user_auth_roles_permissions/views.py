from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import Role, RolePermission
from .serializers import (
    RoleSerializer,
    RolePermissionGridSerializer,
    RolePermissionSerializer,
)


# ── Role CRUD ────────────────────────────────────────────────────────────────
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


# ── RolePermission CRUD ───────────────────────────────────────────────────────
class RolePermissionListCreateView(generics.ListCreateAPIView):
    """
    GET  /role-permissions/           → সব RolePermission লিস্ট।
                                        ?role_id=<pk> দিয়ে ফিল্টার করা যাবে।
    POST /role-permissions/           → নতুন RolePermission তৈরি।
    """
    serializer_class = RolePermissionSerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdminUser]

    def get_queryset(self):
        qs = RolePermission.objects.select_related('role').all()
        role_id = self.request.query_params.get('role_id')
        if role_id:
            qs = qs.filter(role_id=role_id)
        return qs


class RolePermissionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /role-permissions/<pk>/    → একটি RolePermission দেখুন।
    PUT    /role-permissions/<pk>/    → সম্পূর্ণ আপডেট।
    PATCH  /role-permissions/<pk>/    → আংশিক আপডেট।
    DELETE /role-permissions/<pk>/    → মুছে ফেলুন।
    """
    queryset = RolePermission.objects.select_related('role').all()
    serializer_class = RolePermissionSerializer
    # authentication_classes = [JWTAuthentication]
    # permission_classes = [IsAdminUser]


class AvailableFeaturesAPIView(APIView):
    """
    settings.INSTALLED_APPS এবং APP_FEATURES থেকে জেনারেট হওয়া 
    সব অ্যাপ ও ফিচারের কমপ্লিট লিস্ট গ্রিড UI রেন্ডার করার জন্য পাঠাবে।
    """
    def get(self, request, *args, **kwargs):
        features_data = RolePermission.get_all_app_features()
        return Response(features_data, status=status.HTTP_200_OK)


# ২. নির্দিষ্ট রোলের আন্ডারে অ্যাপ ভিত্তিক ফিচারের পারমিশন সেট বা বাল্ক আপডেট করার API
class AssignFeaturePermissionsAPIView(APIView):
    def post(self, request, *args, **kwargs):
        role_name = request.data.get('role_name')
        permissions_data = request.data.get('permissions', [])

        if not role_name:
            return Response({"error": "role_name is required"}, status=status.HTTP_400_BAD_REQUEST)

        role_obj, _ = Role.objects.get_or_create(name=role_name.strip().capitalize())

        for item in permissions_data:
            feature_name = item.get('feature_name')
            feature_slug = item.get('feature_slug')
            
            if not feature_name or not feature_slug:
                continue
                
            allow_all = item.get('allow_all', False)
            
            RolePermission.objects.update_or_create(
                role=role_obj,
                feature_name=feature_name.strip(),
                feature_slug=feature_slug.strip(),
                defaults={
                    'can_create': True if allow_all else item.get('can_create', False),
                    'can_view': True if allow_all else item.get('can_view', False),
                    'can_edit': True if allow_all else item.get('can_edit', False),
                    'can_delete': True if allow_all else item.get('can_delete', False),
                }
            )

        # এখানে RoleDetailWithPermissionsSerializer এর জায়গায় সরাসরি আপনার RoleSerializer ব্যবহার করা হয়েছে
        serializer = RoleSerializer(role_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)
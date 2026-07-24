from rest_framework import serializers
from .models import User
from user_auth_roles_permissions.models import Role
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        user = self.user

        role = getattr(user, "user_role", None)

        permissions = []

        if role:
            permissions = [
                {
                    "feature_name": p.feature_name,
                    "feature_slug": p.feature_slug,
                    "can_create": p.can_create,
                    "can_view": p.can_view,
                    "can_edit": p.can_edit,
                    "can_delete": p.can_delete,
                }
                for p in role.role.feature_permissions.all()
            ]

        data["user"] = {
            "id": user.id,
            "username": user.username,
            "name": user.name,
            "role": {
                "id": role.role.id,
                "name": role.role.name,
            } if role else None,
            "permissions": permissions,
        }

        return data

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6, required=False)
    
    class Meta:
        model = User
        fields = ['id', 'name', 'username', 'phone_number', 'password']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        validated_data.pop('password', None)
        return super().update(instance, validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True, min_length=6)
    confirm_password = serializers.CharField(write_only=True)
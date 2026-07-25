# views.py
from rest_framework.generics import ListAPIView, CreateAPIView, UpdateAPIView, DestroyAPIView
from .serializers import UserRegistrationSerializer, ChangePasswordSerializer
from rest_framework import status
from rest_framework.response import Response
from .models import User
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer, UserRoleAssignSerializer
from user_auth_roles_permissions.models import Role
from .models import UserRole

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

#user list
class userlistview(ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer    


#user registration class
class UserRegistrationView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer       

    def perform_create(self, serializer):
        """
        user save
        """
        serializer.save()


#user info (name, username, phone_number, role) update class
class UpdateUserInfoView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    lookup_field = 'pk'
    http_method_names = ['patch']   # শুধু PATCH, PUT বন্ধ


#change password class (আলাদা, শুধু password এর জন্য)
class ChangePasswordView(UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = ChangePasswordSerializer
    lookup_field = 'pk'
    http_method_names = ['patch']   # শুধু PATCH, PUT বন্ধ

    def update(self, request, *args, **kwargs):
        instance = self.get_object()

        old_password = request.data.get('old_password')
        new_password = request.data.get('password')
        confirm_password = request.data.get('confirm_password')

        if not old_password or not new_password or not confirm_password:
            return Response(
                {"detail": "old_password, password, confirm_password — সবগুলো field দিতে হবে।"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not instance.check_password(old_password):
            return Response(
                {"detail": "Old password is incorrect."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_password != confirm_password:
            return Response(
                {"detail": "New password and confirm password do not match."},
                status=status.HTTP_400_BAD_REQUEST
            )

        instance.set_password(new_password)
        instance.save()

        return Response({"detail": "Password changed successfully."}, status=status.HTTP_200_OK)


#user profile delete class
class UserProfileDeleteview(DestroyAPIView):
    queryset = User.objects.all()  #all user call
    serializer_class = UserRegistrationSerializer  #serializer class call serializer
    lookup_field = 'id'


class UserRoleAssignView(CreateAPIView):
    """
    POST /assign-role/
    {
        "user_id": 1,
        "role_id": 2
    }
    Assigns or updates a role for a given user.
    """
    serializer_class = UserRoleAssignSerializer
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user_id = serializer.validated_data['user_id']
        role_id = serializer.validated_data['role_id']
        
        try:
            user = User.objects.get(id=user_id)
            role = Role.objects.get(id=role_id)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        except Role.DoesNotExist:
            return Response({"error": "Role not found."}, status=status.HTTP_404_NOT_FOUND)
            
        # Update UserRole model
        user_role, created = UserRole.objects.update_or_create(
            user=user,
            defaults={'role': role}
        )
        
        # Also update the role field in User model for consistency
        user.role = role
        user.save()
        
        return Response({
            "message": "Role assigned successfully.",
            "user_id": user.id,
            "role_id": role.id,
            "role_name": role.name
        }, status=status.HTTP_200_OK)
from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path(
        "login-new/",
        CustomTokenObtainPairView.as_view(),
        name="token_obtain_pair",
    ),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('Userlist/', userlistview.as_view(), name='user-list'),
    path('update-user-info/<int:pk>/', UpdateUserInfoView.as_view(), name='update-user-info'),
    path('change-password/<int:pk>/', ChangePasswordView.as_view(), name='change-password'),
    path('delete-profile/<int:id>/', UserProfileDeleteview.as_view(), name='delete-profile'),
]
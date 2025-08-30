from django.urls import path
from .views import *
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)


urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('Userlist/', userlistview.as_view(), name='user-list'),
    path('update-user-password/<int:pk>/', UpdateUsernamepassView.as_view(), name='update-user'),
    path('delete-profile/<int:id>/', UserProfileDeleteview.as_view(), name='delete-profile'),

]

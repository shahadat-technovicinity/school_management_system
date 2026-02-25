from rest_framework.routers import DefaultRouter
from .views import StudentIDCardViewSet
from django.urls import path, include

router = DefaultRouter()
router.register(r'id-cards', StudentIDCardViewSet, basename='id-cards')

urlpatterns = [
    path('api/', include(router.urls)),
]
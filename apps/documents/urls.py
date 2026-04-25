from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.certificate_views import CertificateApplicationViewSet

router = DefaultRouter()
router.register(r'certificates', CertificateApplicationViewSet, basename='certificate-application')

urlpatterns = [
    path('', include(router.urls)),
]

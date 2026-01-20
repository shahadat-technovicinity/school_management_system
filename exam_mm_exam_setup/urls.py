# exam / urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r"", ExamSetupViewSet, basename="exam")

urlpatterns = [
    path("", include(router.urls)),
]
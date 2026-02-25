from rest_framework.routers import DefaultRouter
from .views import StudentIDCardViewSet,task_status
from django.urls import path, include

router = DefaultRouter()
router.register(r'id-cards', StudentIDCardViewSet, basename='id-cards')

urlpatterns = [
    path('', include(router.urls)),
    path('task-status/<str:task_id>/', task_status, name='task-status'),
]
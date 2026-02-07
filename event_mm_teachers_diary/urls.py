from django.urls import path
from .views import *

urlpatterns = [
    path('entries/', DiaryListCreateView.as_view(), name='diary-list-create'),
    path('entries/<int:pk>/', DiaryDetailView.as_view(), name='diary-detail'),
]
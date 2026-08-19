from django.urls import path
from .views import NothiListView, NothiDetailView

urlpatterns = [
    path('', NothiListView.as_view(), name='nothi-list'),
    path('<int:pk>/', NothiDetailView.as_view(), name='nothi-detail'),
]
from django.urls import path
from .views import StockListCreateAPIView, StockDetailAPIView

urlpatterns = [
    path('inventory/', StockListCreateAPIView.as_view(), name='inventory-list'),
    path('inventory/<int:pk>/', StockDetailAPIView.as_view(), name='inventory-detail'),
]
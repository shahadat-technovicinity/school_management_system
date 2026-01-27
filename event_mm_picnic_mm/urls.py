from django.urls import path
from .views import *

urlpatterns = [
    path('picnics/', PicnicListCreateAPIView.as_view(), name='picnic-list-create'),
    path('picnics/<int:id>/', PicnicRetrieveUpdateDestroyAPIView.as_view(), name='picnic-detail'),
]
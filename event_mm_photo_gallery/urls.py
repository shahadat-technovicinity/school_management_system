from django.urls import path
from .views import *

urlpatterns = [
    ## Photo Gallery URLs
    path('photos/', PhotoListCreateView.as_view(), name='photo-list-create'),
    path('photos/<int:pk>/', PhotoRetrieveUpdateDeleteView.as_view(), name='photo-detail'),

    ## Video Gallery URLs
    
    path('videos/', VideoListCreateView.as_view(), name='video-list-create'),
    path('videos/<int:pk>/', VideoRetrieveUpdateDeleteView.as_view(), name='video-detail'),
]
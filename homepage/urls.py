from django.urls import path
from .views import *
urlpatterns = [
    ### slider urls
    path('sliders/', Home_Page_SliderListCreateView.as_view(), name='slider-list-create'),
    path('sliders/<int:pk>/', Home_Page_SliderRetrieveUpdateDestroyView.as_view(), name='slider-detail'),

    ## Message urls
    path('messages/', MessageListCreateView.as_view(), name='message-list-create'),
    path('messages/<int:pk>/', MessageRetrieveUpdateDestroyView.as_view(), name='message-detail'),
]
from django.urls import path
from .views import *
urlpatterns = [
    ### slider urls
    path('sliders/', Home_Page_SliderListCreateView.as_view(), name='slider-list-create'),
    path('sliders/<int:pk>/', Home_Page_SliderRetrieveUpdateDestroyView.as_view(), name='slider-detail'),

    ## Message urls
    path('messages/', MessageListCreateView.as_view(), name='message-list-create'),
    path('messages/<int:pk>/', MessageRetrieveUpdateDestroyView.as_view(), name='message-detail'),


    ## Admission Notice urls
    path('admissionnotices/', AdmissionNoticeListCreateView.as_view(), name='admissionnotice-list-create'),
    path('admissionnotices/<int:pk>/', AdmissionNoticeRetrieveUpdateDestroyView.as_view(), name='admissionnotice-detail'),


    ## Contact Message urls
    path('contactmessages/', ContactMessageListCreateView.as_view(), name='contactmessage-list-create'),
    path('contactmessages/<int:pk>/', ContactMessageRetrieveUpdateDestroyView.as_view(), name='contactmessage-detail'),


    ## Letter Info urls
    path('letterinfos/', LetterInfoListCreateView.as_view(), name='letterinfo-list-create'),
    path('letterinfos/<int:pk>/', LetterInfoRetrieveUpdateDestroyView.as_view(), name='letterinfo-detail'),
]
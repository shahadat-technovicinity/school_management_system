from django.urls import path
from .views import *
urlpatterns = [
    ### Notice URLs for Communication Center
    path('notices/', NoticeListCreateAPIView.as_view(), name='notice-list-create'),
    path('notices/<int:pk>/', NoticeDetailAPIView.as_view(), name='notice-detail'),


    ### Letter Issue URLs for Communication Center
    path('letters/', LetterIssueListCreateAPIView.as_view(), name='letter-issue-list-create'),

]
from django.urls import path
from .views import MailListView, MailCreateView, MailDetaiilllView

urlpatterns = [
    path('mails/', MailListView.as_view(), name='mail-list'),
    path('mails/send/', MailCreateView.as_view(), name='mail-send'),
    path('mails/<int:pk>/', MailDetaiilllView.as_view(), name='mail-detail'),
]







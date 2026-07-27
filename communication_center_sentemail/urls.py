from django.urls import path
from .views import MailListView, MailCreateView, MailDetailView

urlpatterns = [
    path('mails/', MailListView.as_view(), name='mail-list'),
    path('mails/send/', MailCreateView.as_view(), name='mail-send'),
    path('mails/<int:pk>/', MailDetailView.as_view(), name='mail-detail'),
]







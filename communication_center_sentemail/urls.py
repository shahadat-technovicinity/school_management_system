from django.urls import path
from .views import (
    UserListView,
    MailListView,
    MailCreateView,
    MailDetailView,
    MailDeleteView,
    MailStarToggleView,
    MailMoveFolderView,
    MailReplyView,
    UnreadCountView,
)

urlpatterns = [
    # path('users/', UserListView.as_view(), name='mail-users'),
    path('mails/', MailListView.as_view(), name='mail-list'),
    path('mails/create/', MailCreateView.as_view(), name='mail-create'),
    # path('mails/<int:pk>/', MailDetailView.as_view(), name='mail-detail'),
    path('mails/<int:pk>/delete/', MailDeleteView.as_view(), name='mail-delete'),
    path('mails/<int:pk>/star/', MailStarToggleView.as_view(), name='mail-star'),
    path('mails/<int:pk>/move/', MailMoveFolderView.as_view(), name='mail-move'),
    path('mails/<int:pk>/reply/', MailReplyView.as_view(), name='mail-reply'),
    path('mails/unread-count/', UnreadCountView.as_view(), name='mail-unread-count'),
]
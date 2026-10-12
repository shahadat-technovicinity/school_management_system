from django.urls import path
from .views import (
    SendFlexibleSMSView,
    SMSHistoryListView,
    CheckSMSBalanceView
)

urlpatterns = [
    path('sms/send/', SendFlexibleSMSView.as_view(), name='sms-send'),
    path('sms/history/', SMSHistoryListView.as_view(), name='sms-history'),
    path('sms/balance/', CheckSMSBalanceView.as_view(), name='sms-balance'),
]
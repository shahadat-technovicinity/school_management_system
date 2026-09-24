from django.urls import path
from .views import (
    SendFlexibleSMSView,
    SMSTemplateListCreateView,
    SMSTemplateDetailView,
    SMSHistoryListView,
    CheckSMSBalanceView
)

urlpatterns = [
    path('sms/send/', SendFlexibleSMSView.as_view(), name='sms-send'),
    path('sms/templates/', SMSTemplateListCreateView.as_view(), name='sms-template-list'),
    path('sms/templates/<int:pk>/', SMSTemplateDetailView.as_view(), name='sms-template-detail'),
    path('sms/history/', SMSHistoryListView.as_view(), name='sms-history'),
    path('sms/balance/', CheckSMSBalanceView.as_view(), name='sms-balance'),
]
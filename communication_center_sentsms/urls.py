from django.urls import path
from .views import (
    SMSTemplateListCreateView,
    SMSTemplateDetailView,
    SendSMSView,
    SMSSentHistoryListView,
    SMSStatsView,
    SMSBalanceView,
    SMSReportView,
)

urlpatterns = [
    path('sms-templates/', SMSTemplateListCreateView.as_view(), name='template-list-create'),
    path('sms-templates/<int:pk>/', SMSTemplateDetailView.as_view(), name='template-detail'),
    path('sms/send/', SendSMSView.as_view(), name='sms-send'),
    path('sms/history/', SMSSentHistoryListView.as_view(), name='sms-history'),
    path('sms/stats/', SMSStatsView.as_view(), name='sms-stats'),
    path('sms/balance/', SMSBalanceView.as_view(), name='sms-balance'),
    path('sms/report/<str:request_id>/', SMSReportView.as_view(), name='sms-report'),
]
from django.urls import path
from .views import SMSTemplateListCreateView, SMSTemplateDetailView

urlpatterns = [
    path('sms-templates/', SMSTemplateListCreateView.as_view(), name='template-list-create'),
    path('sms-templates/<int:pk>/', SMSTemplateDetailView.as_view(), name='template-detail'),
]
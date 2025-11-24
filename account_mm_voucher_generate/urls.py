# urls.py (Finance App)

from django.urls import path
from .views import *
urlpatterns = [
      path('vouchers_generate/', GenerateVoucherAPIView.as_view(), name='list_create_voucher'),
]

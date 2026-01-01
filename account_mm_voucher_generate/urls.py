# urls.py (Finance App)

from django.urls import path
from .views import *
urlpatterns = [
      path('vouchers_generate/', GenerateVoucherAPIView.as_view(), name='list-create-voucher'),
      path('vouchers_delete/<int:pk>/', DeleteVoucherAPIView.as_view(), name='voucher-delete'),

#     # 2. GET Method: To download the generated PDF using the saved voucher ID (pk)
#     path('finance/voucher/generate/<int:pk>/', VoucherGenerateAPIView.as_view(), name='voucher-pdf-download'),
]
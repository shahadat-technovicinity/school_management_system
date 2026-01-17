from django.urls import path
from .views import *

urlpatterns = [
    path('furniture/', Facility_asset.as_view(), name='furniture'),
    path('furniture_update_delete/<int:pk>/', Facility_assetupdatedelete.as_view(), name='furniture'),
    path('asset_summary/', AssetSummaryView.as_view(), name='asset_summary')
]


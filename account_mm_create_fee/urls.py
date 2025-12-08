from django.urls import path
from .views import *


urlpatterns = [
    path("create_free/", FeeCreate.as_view(), name="create_free"),
    # path("create_view_fee/", CreateFeeListCreateAPIView.as_view(), name="create_free"),

]
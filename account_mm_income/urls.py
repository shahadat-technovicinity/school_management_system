from django.urls import path
from .views import *

urlpatterns = [
    path('income_collect/', income_collect.as_view(), name = "stu_step"),
    path('income_updatedelete/<int:pk>/', income_collect_retrievedestroy.as_view(), name = "stu_stepdestroy"),

]
from django.urls import path
from .views import *

urlpatterns = [
    path('BookDistributionCreate_get_api/', BookDistributionCreate_get_api.as_view()),
    path('BookDistribution_get_update_delete_api/<int:pk>/', BookDistribution_get_update_delete_api.as_view()),
    path('Letter_list_create_api/', Letter_list_create_api.as_view()),
    path('Letter_update_delete_api/<int:pk>/', Letter_update_delete_api.as_view()),
]
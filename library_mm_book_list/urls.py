from django.urls import path
from .views import *

urlpatterns = [
    path('book_list_create/', Book_list_create_get_api.as_view()),
    path('book_get_update_delete/<int:pk>/', Book_model_get_update_delete_api.as_view())
]
from django.urls import path, include
from .views import *


urlpatterns = [
    path('register_student_profile_info/', StudentProfileCreate.as_view(), name='register'),  #New student form route
    path('addmissionexamrud/<int:pk>/', StudentProfileUpdateDelete.as_view(), name='delete-admissionexam'),

]
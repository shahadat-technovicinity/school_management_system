from django.urls import path, include
from .views import *


urlpatterns = [
    path('register_student_info/', stident_info_createapiview.as_view(), name='register'),  #New student form route
    path('student_info/', student_info_get.as_view(), name='studentinfo'),                  #form student get route

]
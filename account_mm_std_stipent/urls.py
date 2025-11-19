from django.urls import path
from .views import *

urlpatterns = [
    path('stipend_student/', stipent_student_listcreate.as_view(), name = "stu_step"),
    path('stipend_student_retrievedestroy/<int:pk>/', stipent_student_retrievedestroy.as_view(), name = "stu_stepdestroy"),

]
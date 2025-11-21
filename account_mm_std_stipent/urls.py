from django.urls import path
from .views import *

urlpatterns = [
    path('stipend_student/', stipent_student_listcreate.as_view(), name = "stu_step"),
    path('stipend_student_retrievedestroy/<int:pk>/', stipent_student_retrievedestroy.as_view(), name = "stu_stepdestroy"),

    path('stipend_free_hf/', stipent_free_hf_listcreate.as_view(), name = "freehf_step"),
    path('stipend_free_hf_destroyretrivew/<int:pk>/', stipent_free_hf_retrievedestroy.as_view(), name = "freehf_stepdestroy"),

]
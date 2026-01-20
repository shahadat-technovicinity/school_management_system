from django.urls import path, include
from .views import *


urlpatterns = [
    path('std_admission_exam/', std_admission_exam.as_view(), name='register'),  #New student form route
    # path('student_info/', student_exam_get.as_view(), name='studentinfo'),                  #form student get route
    # path('delete-admission-exam/<int:id>/', addmissionexamdelete.as_view(), name='delete-admissionexam'),
    path('addmissionexamrud/<int:pk>/', StdExmRetrieveUpdateDestroyAPIView.as_view(), name='delete-admissionexam'),

]
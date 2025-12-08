from django.urls import path, include
from .views import *


urlpatterns = [
    path('TeacherStaffList/', TeacherStaffListView.as_view(), name='register'),  #New student form route
    path("TeacherStaffWorkView/", TeacherStaffWorkView.as_view(), name="TeacherStaffWorkView"),  # This url is get and post
    path('TeacherStaffWorkUpdateDelete/<int:pk>/', TeacherStaffWorkUpdateDelete.as_view(), name='updatedelete'),  #this route is get, update, delete
]
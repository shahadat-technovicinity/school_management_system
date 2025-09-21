from django.urls import path
from .views import *

urlpatterns = [
    path("academicoc/", Onlineclass.as_view(), name="online-class-list"),
    path("academic_online_class_delete/<int:id>", onlineclassdelete.as_view(), name="aoc-delete"),

]
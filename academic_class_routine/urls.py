from django.urls import path
from .views import *

urlpatterns = [
    path("teachers/", TeacherListView.as_view(), name="teacher-list"),  # this url is teacher get
    # path("ClassRoutine/", ClassRoutineCreate.as_view(), name="RoutineList"),
    path("classRoutine/", ClassRoutineView.as_view(), name="RoutineapiList"),  # This url is get and post
    path('academicclassroutine/<int:pk>/', ClassRoutineupdateDelete.as_view(), name='updatedelete'),  #this route is get, update, delete

]

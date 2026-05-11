from django.urls import path
from .views import BANBEISEnrollmentView, BANBEISTeacherInfoView

urlpatterns = [
    path('banbeis/enrollment/', BANBEISEnrollmentView.as_view(), name='banbeis-enrollment'),
    path('banbeis/teacher-info/', BANBEISTeacherInfoView.as_view(), name='banbeis-teacher-info'),
]
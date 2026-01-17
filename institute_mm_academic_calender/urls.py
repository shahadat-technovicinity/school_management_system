from django.urls import path 
from .views import *


urlpatterns = [
    path('academic_calendar/', AcademicCalendarListCreateView.as_view(), name='academic_calendar'),
    path('academic_calendar/<int:pk>/', AcademicCalendarRetrieveUpdateDestroyView.as_view(), name='academic_calendar_detail'),
    path('holiday/', HolidayListCreateView.as_view(), name='holiday'),
    path('holiday/<int:pk>/', HolidayRetrieveUpdateDestroyView.as_view(), name='holiday_detail'),
]
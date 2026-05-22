from django.urls import path
from .views import (
    QuickEntryView,
    CheckOutView,
    TodayAttendanceView,
    StudentsInLibraryView,
    HistoricalAttendanceView,
    LibraryAttendanceDestroyView,
)

urlpatterns = [
    path('library/quick-entry/', QuickEntryView.as_view(), name='library-quick-entry'),
    path('library/checkout/<int:pk>/', CheckOutView.as_view(), name='library-checkout'),
    path('library/today/', TodayAttendanceView.as_view(), name='library-today'),
    path('library/in-library/', StudentsInLibraryView.as_view(), name='students-in-library'),
    path('library/history/', HistoricalAttendanceView.as_view(), name='library-history'),
    path('library/<int:pk>/', LibraryAttendanceDestroyView.as_view(), name='library-detail'),
]

from django.urls import path
from .views import *

urlpatterns = [
    path('students/filter/', StudentFilterView.as_view(), name='student-filter'),
    path('marksadd/', MarksListCreateAPIView.as_view(), name='studentmarkadd'),
    path('FinalResultView/', FinalResultView.as_view(), name='studentmarkadd'),
    path('resultupdate/<int:pk>/', MarkRetrieveUpdateDestroyAPIView.as_view(), name='admin-change-status'),

]

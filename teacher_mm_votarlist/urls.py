# urls.py
from django.urls import path
from .views import ParentVoterListView

urlpatterns = [
    path('voter-list/', ParentVoterListView.as_view(), name='parent-voter-list'),
]
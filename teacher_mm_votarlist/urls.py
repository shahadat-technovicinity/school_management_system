from django.urls import path
from .views import ParentVoterListView, ExportParentVoterListExcelView

urlpatterns = [
    path('voter-list/', ParentVoterListView.as_view(), name='parent-voter-list'),
    path('voter-list/export-excel/', ExportParentVoterListExcelView.as_view(), name='export-parent-voter-list-excel'),
]
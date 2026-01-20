from django.urls import path
from .views import *


urlpatterns = [
    path('create_view_comitee/', CommitteeMemberViewCreate.as_view(), name='create_view_comitee'),
    path('TeacherStaffWorkUpdateDelete/<int:pk>/', CommitteeMemberDelUp.as_view(), name='updatedelete'),
    path('CommitteeMemberDashboard/', CommitteeDashboardView.as_view(), name='committee-members'),
    path('CommitteeMemberListViews/', CommitteeMemberListView.as_view(), name='create_view_comitee'),


]



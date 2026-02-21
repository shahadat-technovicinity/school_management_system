from django.urls import path
from .views import *

urlpatterns = [
    ## Magazine Issue URLs
    path('megazine_create_issue/', MagazineIssueCreateView.as_view(), name='create-issue'),
    path('megazine_update_issue/<int:pk>/', MagazineUpdateDeleteView.as_view(), name='update-delete-issue'),

    ## New URLs for Scheduled Publication
    path('schedule_publication/', SchedulePublicationCreateView.as_view(), name='schedule-publication'),
    path('schedule_publication/<int:pk>/', SchedulePublicationUpdateDeleteView.as_view(), name='update-delete-schedule-publication'),

    ## New URLs for Content Submission
    path('content_submission/', ContentSubmissionCreateView.as_view(), name='content-submission'),
    path('content_submission/<int:pk>/', ContentSubmissionUpdateDeleteView.as_view(), name='update-delete-content-submission'),
]
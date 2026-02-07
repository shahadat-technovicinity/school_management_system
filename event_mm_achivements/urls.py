from django.urls import path
from .views import *

urlpatterns = [
    # Main cards list ar creation
    path('achievements/', AchievementListCreateView.as_view(), name='achievement-list-create'),
    
    # Upore thaka blue, green, yellow card stats
    path('achievements/stats/', AchievementStatsView.as_view(), name='achievement-stats'),

    # Specific edit/delete logic
    path('achievements/<int:pk>/', AchievementDetailView.as_view(), name='achievement-detail'),
]
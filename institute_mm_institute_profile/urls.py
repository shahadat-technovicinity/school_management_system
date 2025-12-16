from django.urls import path
from .views import *


urlpatterns = [
    path('institutions/', InstitutionListCreateView.as_view(), name='institution-list-create'),
    path('institutions/<int:pk>/', InstitutionInfoView.as_view(), name='institution-detail'),
]
from django.urls import path
from .views import *


urlpatterns = [
    #Instituteinfobasic
    path('institutions/', InstitutionListCreateView.as_view(), name='institution-list-create'),
    path('institutions/<int:pk>/', InstitutionInfoView.as_view(), name='institution-detail'),
   
   
   #Instituteinfobank
    path('institute_bank/', InstitutionBankListCreateView.as_view(), name='institution-list-create'),
    path('institute_bank/<int:pk>/', Institutebankupdatedelete.as_view(), name='institution-detail'),

    #Instituteinfobank
    path('institute_others/', InstitutionothersListCreateView.as_view(), name='institution-list-create'),
    path('institute_others/<int:pk>/', Instituteothersupdatedelete.as_view(), name='institution-detail'),
]



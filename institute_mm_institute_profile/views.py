from django.shortcuts import render
from rest_framework import generics
from .serializers import *
from .models import *

# institute info.
class InstitutionListCreateView(generics.ListCreateAPIView):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer


class InstitutionInfoView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Institution.objects.all()
    serializer_class = InstitutionSerializer
    


#########Institute details page
class InstitutiondetailsListCreateView(generics.ListCreateAPIView):
    queryset = InstitutionDetails.objects.all()
    serializer_class = InstitutionDetailsSerializer


class InstitutionDetailpageView(generics.RetrieveUpdateDestroyAPIView):
    queryset = InstitutionDetails.objects.all()
    serializer_class = InstitutionDetailsSerializer



#########Institute bank
class InstitutionBankListCreateView(generics.ListCreateAPIView):
    queryset = InstituteInfoBank.objects.all()
    serializer_class = InstituteBankSerializer


class Institutebankupdatedelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = InstituteInfoBank.objects.all()
    serializer_class = InstituteBankSerializer



#########Institute others
class InstitutionothersListCreateView(generics.ListCreateAPIView):
    queryset = InstituteOthers.objects.all()
    serializer_class = InstituteOthersSerializer


class Instituteothersupdatedelete(generics.RetrieveUpdateDestroyAPIView):
    queryset = InstituteOthers.objects.all()
    serializer_class = InstituteOthersSerializer





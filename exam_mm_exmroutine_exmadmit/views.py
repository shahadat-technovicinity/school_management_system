from django.shortcuts import render

from rest_framework import generics
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count, Q

class ExamRoutineListCreateView(generics.ListCreateAPIView):
    queryset = ExamRoutine.objects.all()
    serializer_class = ExamRoutineAdmit


class ExamRoutineDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExamRoutine.objects.all()
    serializer_class = ExamRoutineAdmit


####admit header

class ExamAdmitListCreateView(generics.ListCreateAPIView):
    queryset = ExamAdmit.objects.all()
    serializer_class = ExamAdmitSerializer


class ExamAdmitDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ExamAdmit.objects.all()
    serializer_class = ExamAdmitSerializer



########## admit card generate summary dashboard api ######
class AdmitCardSummaryDashboardAPIView(APIView):
    def get(self, request):
        generated = ExamAdmit.objects.filter(payment_status='paid').count()
        pending = ExamAdmit.objects.filter(payment_status='non paid').count()

        data = {
            'generated': generated,
            'pending': pending
        }
        return Response(data)
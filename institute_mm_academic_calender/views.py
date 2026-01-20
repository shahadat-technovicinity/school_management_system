from django.shortcuts import render
from rest_framework.response import Response
from .models import *
from . serializers import *
from rest_framework import generics



# Create your views here.
class AcademicCalendarListCreateView(generics.ListCreateAPIView):
    queryset = AcademicCalendar.objects.all()
    serializer_class = AcademicCalendarSerializer

class AcademicCalendarRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = AcademicCalendar.objects.all()
    serializer_class = AcademicCalendarSerializer



class HolidayListCreateView(generics.ListCreateAPIView):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer

class HolidayListCreateView(generics.ListCreateAPIView):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
    def list(self, request, *args, **kwargs):
        holidays = self.get_queryset()
        
        custom_data = []
        for h in holidays:
            data = self.get_serializer(h).data
            data['duration'] = (h.end_date - h.start_date).days + 1
            custom_data.append(data)

        return Response(custom_data)
    

class HolidayRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Holiday.objects.all()
    serializer_class = HolidaySerializer
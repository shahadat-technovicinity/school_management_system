from rest_framework import generics
from datetime import date, timedelta
from .models import *
from .serializers import *
from rest_framework.pagination import PageNumberPagination

class MyPagination(PageNumberPagination):
    page_size = 10

class BookDistributionCreate_get_api(generics.ListCreateAPIView):
    serializer_class = BookDistributionModelSerializer
    pagination_class = MyPagination

    def get_queryset(self):
        # Default bhabe shob data nibe ar order korbe
        queryset = BookDistributionModel.objects.all().order_by('-created_at')

        # URL theke parameters gulo dhorbe
        filter_type = self.request.query_params.get('filter') # e.g. ?filter=today
        from_date = self.request.query_params.get('from_date') # e.g. ?from_date=2026-01-01
        to_date = self.request.query_params.get('to_date')

        today = date.today()

        # 1. Quick Filters (Today, Week, Month)
        if filter_type == 'today':
            queryset = queryset.filter(created_at__date=today)

        elif filter_type == 'week':
            last_week = today - timedelta(days=7)
            queryset = queryset.filter(created_at__date__gte=last_week)

        elif filter_type == 'month':
            queryset = queryset.filter(created_at__year=today.year, created_at__month=today.month)

        # 2. Date Range Filter (Custom Date selection)
        if from_date and to_date:
            queryset = queryset.filter(created_at__date__range=[from_date, to_date])

        return queryset

class BookDistribution_get_update_delete_api(generics.RetrieveUpdateDestroyAPIView):
    queryset = BookDistributionModel.objects.all()
    serializer_class = BookDistributionModelSerializer






# 1. Letter: List and Create
class Letter_list_create_api(generics.ListCreateAPIView):
    queryset = LetterDistribution.objects.all().order_by('-date_sent')
    serializer_class = LetterDistributionSerializer
    pagination_class = MyPagination

# 2. Letter: Retrieve, Update and Delete
class Letter_update_delete_api(generics.RetrieveUpdateDestroyAPIView):
    queryset = LetterDistribution.objects.all()
    serializer_class = LetterDistributionSerializer
from rest_framework import generics, filters, pagination, parsers
from .models import CrimeReport
from .serializers import CrimeReportSerializer


class CrimeReportPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class CrimeReportListCreateView(generics.ListCreateAPIView):
    queryset = CrimeReport.objects.all()
    serializer_class = CrimeReportSerializer
    pagination_class = CrimeReportPagination
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['case_number', 'plaintiff', 'defendant', 'subject']


class CrimeReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CrimeReport.objects.all()
    serializer_class = CrimeReportSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
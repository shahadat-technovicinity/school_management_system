from rest_framework import generics, filters, pagination, parsers
from .models import VisitingReport
from .serializers import VisitingReportSerializer


class VisitingReportPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class VisitingReportListCreateView(generics.ListCreateAPIView):
    queryset = VisitingReport.objects.all()
    serializer_class = VisitingReportSerializer
    pagination_class = VisitingReportPagination
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
    filter_backends = [filters.SearchFilter]
    search_fields = ['officer_name', 'designation', 'office', 'remarks']


class VisitingReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = VisitingReport.objects.all()
    serializer_class = VisitingReportSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]
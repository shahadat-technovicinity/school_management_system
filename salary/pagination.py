"""
Salary Management Pagination

Custom pagination classes for salary endpoints.
"""

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class SalaryPagination(PageNumberPagination):
    """
    Standard pagination for salary list.
    """
    page_size = 10
    page_size_query_param = "per_page"
    max_page_size = 100
    page_query_param = "page"

    def get_paginated_response(self, data):
        return Response({
            "status": "success",
            "count": self.page.paginator.count,
            "total_pages": self.page.paginator.num_pages,
            "current_page": self.page.number,
            "per_page": self.get_page_size(self.request),
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data,
        })


class SalaryExportPagination(PageNumberPagination):
    """
    Larger pagination for export operations.
    """
    page_size = 1000
    page_size_query_param = "per_page"
    max_page_size = 5000

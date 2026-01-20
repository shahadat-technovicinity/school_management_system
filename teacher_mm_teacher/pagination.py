from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class TeacherPagination(PageNumberPagination):
    """
    Custom pagination class for Teacher list endpoint.
    
    Features:
    - Default page size: 10
    - Maximum page size: 100
    - Client can specify page size via 'page_size' query parameter
    - Returns additional metadata in response
    """

    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100
    page_query_param = "page"

    def get_paginated_response(self, data):
        """
        Return a paginated response with additional metadata.
        """
        return Response({
            "count": self.page.paginator.count,
            "total_pages": self.page.paginator.num_pages,
            "current_page": self.page.number,
            "page_size": self.get_page_size(self.request),
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data,
        })

    def get_paginated_response_schema(self, schema):
        """
        Return the schema for paginated response (for Swagger documentation).
        """
        return {
            "type": "object",
            "properties": {
                "count": {
                    "type": "integer",
                    "description": "Total number of results",
                    "example": 50,
                },
                "total_pages": {
                    "type": "integer",
                    "description": "Total number of pages",
                    "example": 5,
                },
                "current_page": {
                    "type": "integer",
                    "description": "Current page number",
                    "example": 1,
                },
                "page_size": {
                    "type": "integer",
                    "description": "Number of results per page",
                    "example": 10,
                },
                "next": {
                    "type": "string",
                    "nullable": True,
                    "description": "URL to the next page",
                    "example": "http://api.example.com/teachers/?page=2",
                },
                "previous": {
                    "type": "string",
                    "nullable": True,
                    "description": "URL to the previous page",
                    "example": None,
                },
                "results": schema,
            },
        }

from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Teacher
from .serializers import (
    TeacherListSerializer,
    TeacherDetailSerializer,
    TeacherCreateSerializer,
    TeacherUpdateSerializer,
)
from .filters import TeacherFilter
from .pagination import TeacherPagination


class TeacherViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Teacher profiles.

    Provides CRUD operations for teacher management:
    - POST /teachers/ - Create a new teacher profile (Admin only)
    - GET /teachers/ - List all teachers with pagination and filtering
    - GET /teachers/{id}/ - Retrieve a single teacher's details
    - PUT/PATCH /teachers/{id}/ - Update a teacher profile
    - DELETE /teachers/{id}/ - Delete a teacher profile

    Supports file uploads for resume, joining letter, and photo.
    """

    queryset = Teacher.objects.select_related("user").all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = TeacherPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TeacherFilter
    search_fields = [
        "teacher_id",
        "user__name",
        "user__username",
        "subject",
        "class_assigned",
        "primary_contact_number",
    ]
    ordering_fields = [
        "teacher_id",
        "user__name",
        "date_of_joining",
        "created_at",
        "status",
    ]
    ordering = ["-created_at"]

    def get_permissions(self):
        """
        Set permissions based on action:
        - list, retrieve: Allow any (or IsAuthenticated based on requirements)
        - create, update, partial_update, destroy: Admin only
        """
        if self.action in ["list", "retrieve"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return TeacherListSerializer
        elif self.action == "retrieve":
            return TeacherDetailSerializer
        elif self.action == "create":
            return TeacherCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return TeacherUpdateSerializer
        return TeacherDetailSerializer

    @swagger_auto_schema(
        operation_description="Create a new teacher profile linked to an existing user",
        operation_summary="Create Teacher",
        request_body=TeacherCreateSerializer,
        responses={
            201: openapi.Response(
                description="Teacher created successfully",
                schema=TeacherDetailSerializer,
            ),
            400: openapi.Response(description="Validation error"),
            401: openapi.Response(description="Authentication required"),
        },
        tags=["Teachers"],
    )
    def create(self, request, *args, **kwargs):
        """
        Create a new teacher profile.

        Links the teacher profile to an existing user account.
        The user must not already have a teacher profile.

        **Required fields:**
        - user_id: ID of the existing user
        - teacher_id: Unique teacher identifier

        **File uploads:**
        - resume: PDF/DOC file
        - joining_letter: PDF/DOC file
        - photo: Image file (JPG, PNG)
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return detailed response
        detail_serializer = TeacherDetailSerializer(serializer.instance)
        headers = self.get_success_headers(detail_serializer.data)
        return Response(
            detail_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @swagger_auto_schema(
        operation_description="Retrieve a paginated list of all teachers with optional filtering",
        operation_summary="List Teachers",
        manual_parameters=[
            openapi.Parameter(
                "search",
                openapi.IN_QUERY,
                description="Search by teacher_id, name, subject, class, or phone",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                description="Filter by status (active, inactive, on_leave)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "gender",
                openapi.IN_QUERY,
                description="Filter by gender (male, female, other)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "subject",
                openapi.IN_QUERY,
                description="Filter by subject",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "class_assigned",
                openapi.IN_QUERY,
                description="Filter by assigned class",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "ordering",
                openapi.IN_QUERY,
                description="Order by field (prefix with - for descending)",
                type=openapi.TYPE_STRING,
            ),
            openapi.Parameter(
                "page",
                openapi.IN_QUERY,
                description="Page number",
                type=openapi.TYPE_INTEGER,
            ),
            openapi.Parameter(
                "page_size",
                openapi.IN_QUERY,
                description="Number of results per page (default: 10, max: 100)",
                type=openapi.TYPE_INTEGER,
            ),
        ],
        responses={
            200: openapi.Response(
                description="List of teachers",
                schema=TeacherListSerializer(many=True),
            ),
        },
        tags=["Teachers"],
    )
    def list(self, request, *args, **kwargs):
        """
        List all teachers with pagination and filtering.

        **Filtering options:**
        - status: Filter by employment status
        - gender: Filter by gender
        - subject: Filter by teaching subject
        - class_assigned: Filter by assigned class
        - contract_type: Filter by contract type
        - work_shift: Filter by work shift

        **Search:**
        Search across teacher_id, name, subject, class, and phone number.

        **Ordering:**
        Order by teacher_id, name, date_of_joining, created_at, or status.
        Use `-` prefix for descending order (e.g., `-created_at`).
        """
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve complete details of a specific teacher",
        operation_summary="Get Teacher Details",
        responses={
            200: openapi.Response(
                description="Teacher details",
                schema=TeacherDetailSerializer,
            ),
            404: openapi.Response(description="Teacher not found"),
        },
        tags=["Teachers"],
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single teacher's complete profile.

        Returns all fields including:
        - Personal information
        - Payroll details
        - Bank information
        - Leave allocation
        - Transport and hostel details
        - Social media links
        - Uploaded documents
        """
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update all fields of a teacher profile",
        operation_summary="Update Teacher",
        request_body=TeacherUpdateSerializer,
        responses={
            200: openapi.Response(
                description="Teacher updated successfully",
                schema=TeacherDetailSerializer,
            ),
            400: openapi.Response(description="Validation error"),
            401: openapi.Response(description="Authentication required"),
            404: openapi.Response(description="Teacher not found"),
        },
        tags=["Teachers"],
    )
    def update(self, request, *args, **kwargs):
        """Update a teacher profile (full update)."""
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partially update a teacher profile",
        operation_summary="Partial Update Teacher",
        request_body=TeacherUpdateSerializer,
        responses={
            200: openapi.Response(
                description="Teacher updated successfully",
                schema=TeacherDetailSerializer,
            ),
            400: openapi.Response(description="Validation error"),
            401: openapi.Response(description="Authentication required"),
            404: openapi.Response(description="Teacher not found"),
        },
        tags=["Teachers"],
    )
    def partial_update(self, request, *args, **kwargs):
        """Partially update a teacher profile."""
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a teacher profile",
        operation_summary="Delete Teacher",
        responses={
            204: openapi.Response(description="Teacher deleted successfully"),
            401: openapi.Response(description="Authentication required"),
            404: openapi.Response(description="Teacher not found"),
        },
        tags=["Teachers"],
    )
    def destroy(self, request, *args, **kwargs):
        """Delete a teacher profile."""
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        method="get",
        operation_description="Get count of teachers by status",
        operation_summary="Teacher Statistics",
        responses={
            200: openapi.Response(
                description="Teacher statistics",
                examples={
                    "application/json": {
                        "total": 50,
                        "active": 45,
                        "inactive": 3,
                        "on_leave": 2,
                    }
                },
            ),
        },
        tags=["Teachers"],
    )
    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Get teacher statistics by status."""
        total = Teacher.objects.count()
        active = Teacher.objects.filter(status="active").count()
        inactive = Teacher.objects.filter(status="inactive").count()
        on_leave = Teacher.objects.filter(status="on_leave").count()

        return Response({
            "total": total,
            "active": active,
            "inactive": inactive,
            "on_leave": on_leave,
        })

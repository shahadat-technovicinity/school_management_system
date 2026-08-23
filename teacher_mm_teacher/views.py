from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import generics
from django.contrib.auth import get_user_model

from .models import Teacher
from .serializers import (
    TeacherListSerializer,
    TeacherDetailSerializer,
    TeacherCreateSerializer,
    TeacherUpdateSerializer,
    TeachersListSerializer,
)
from .filters import TeacherFilter
from .pagination import TeacherPagination

User = get_user_model()


class TeacherViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Teacher profiles.
    """

    # 🟢 Optimized Queryset to avoid N+1 problem
    queryset = Teacher.objects.select_related("user", "subject", "class_assigned").all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = TeacherPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TeacherFilter
    
    # 🟢 Fixed search fields with ForeignKey spans & new Bangla/NID fields
    search_fields = [
        "user__name",
        "user__username",
        "name_bn",
        "subject__name",
        "class_assigned__name",
        "primary_contact_number",
        "nid_number",
    ]
    ordering_fields = [
        "user__name",
        "date_of_joining",
        "created_at",
        "status",
    ]
    ordering = ["-created_at"]

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
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

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
        responses={
            200: openapi.Response(
                description="List of teachers",
                schema=TeacherListSerializer(many=True),
            ),
        },
        tags=["Teachers"],
    )
    def list(self, request, *args, **kwargs):
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


class TeacherListView(generics.ListAPIView):
    """
    Simple Dropdown/List view to populate User options with role 'Teacher'.
    """
    serializer_class = TeachersListSerializer
    pagination_class = None

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return User.objects.none()
            
        return User.objects.filter(role__name__iexact='Teacher')
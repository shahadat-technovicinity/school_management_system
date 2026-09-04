from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import generics
from django.contrib.auth import get_user_model

from .models import TeacherAndStaffProfile
from .serializers import (
    TeacherAndStaffListSerializer,
    TeacherAndStaffDetailSerializer,
    TeacherAndStaffCreateSerializer,
    TeacherAndStaffUpdateSerializer,
    EmployeeUserDropdownSerializer,
)
from .filters import TeacherAndStaffFilter
from .pagination import TeacherAndStaffPagination

User = get_user_model()


class TeacherAndStaffViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Teacher & Staff profiles.
    """

    # Optimized Queryset avoiding N+1 queries
    queryset = TeacherAndStaffProfile.objects.select_related("user").all()
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    pagination_class = TeacherAndStaffPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TeacherAndStaffFilter
    
    search_fields = [
        "user__name",
        "user__username",
        "name_bn",
        "designation",
        "department",
        "primary_contact_number",
        "nid_number",
    ]
    ordering_fields = [
        "user__name",
        "date_of_joining",
        "created_at",
        "status",
        "employee_type",
    ]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return TeacherAndStaffListSerializer
        elif self.action == "retrieve":
            return TeacherAndStaffDetailSerializer
        elif self.action == "create":
            return TeacherAndStaffCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return TeacherAndStaffUpdateSerializer
        return TeacherAndStaffDetailSerializer

    @swagger_auto_schema(
        operation_description="Create a new teacher/staff profile linked to an existing user",
        operation_summary="Create Teacher/Staff Profile",
        request_body=TeacherAndStaffCreateSerializer,
        responses={
            201: openapi.Response(
                description="Profile created successfully",
                schema=TeacherAndStaffDetailSerializer,
            ),
            400: openapi.Response(description="Validation error"),
            401: openapi.Response(description="Authentication required"),
        },
        tags=["Teacher & Staff Profiles"],
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        detail_serializer = TeacherAndStaffDetailSerializer(serializer.instance)
        headers = self.get_success_headers(detail_serializer.data)
        return Response(
            detail_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    @swagger_auto_schema(
        operation_description="Retrieve a paginated list of all teachers and staff with optional filtering",
        operation_summary="List Teachers & Staff",
        responses={
            200: openapi.Response(
                description="List of profiles",
                schema=TeacherAndStaffListSerializer(many=True),
            ),
        },
        tags=["Teacher & Staff Profiles"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve complete details of a specific teacher or staff member",
        operation_summary="Get Teacher/Staff Details",
        responses={
            200: openapi.Response(
                description="Teacher/Staff details",
                schema=TeacherAndStaffDetailSerializer,
            ),
            404: openapi.Response(description="Profile not found"),
        },
        tags=["Teacher & Staff Profiles"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update all fields of a teacher/staff profile",
        operation_summary="Update Teacher/Staff Profile",
        request_body=TeacherAndStaffUpdateSerializer,
        responses={
            200: openapi.Response(
                description="Profile updated successfully",
                schema=TeacherAndStaffDetailSerializer,
            ),
            400: openapi.Response(description="Validation error"),
            401: openapi.Response(description="Authentication required"),
            404: openapi.Response(description="Profile not found"),
        },
        tags=["Teacher & Staff Profiles"],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partially update a teacher/staff profile",
        operation_summary="Partial Update Teacher/Staff Profile",
        request_body=TeacherAndStaffUpdateSerializer,
        responses={
            200: openapi.Response(
                description="Profile updated successfully",
                schema=TeacherAndStaffDetailSerializer,
            ),
            400: openapi.Response(description="Validation error"),
            401: openapi.Response(description="Authentication required"),
            404: openapi.Response(description="Profile not found"),
        },
        tags=["Teacher & Staff Profiles"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a teacher/staff profile",
        operation_summary="Delete Profile",
        responses={
            204: openapi.Response(description="Profile deleted successfully"),
            401: openapi.Response(description="Authentication required"),
            404: openapi.Response(description="Profile not found"),
        },
        tags=["Teacher & Staff Profiles"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        method="get",
        operation_description="Get count of employees categorized by status and type",
        operation_summary="Employee Statistics",
        manual_parameters=[
            openapi.Parameter(
                "employee_type",
                openapi.IN_QUERY,
                description="Filter statistics by 'teacher' or 'staff'",
                type=openapi.TYPE_STRING,
                required=False,
            )
        ],
        responses={
            200: openapi.Response(
                description="Teacher and staff statistics",
                examples={
                    "application/json": {
                        "total": 50,
                        "teachers": 30,
                        "staff": 20,
                        "active": 45,
                        "inactive": 3,
                        "on_leave": 2,
                    }
                },
            ),
        },
        tags=["Teacher & Staff Profiles"],
    )
    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Get employee statistics by status and type."""
        qs = TeacherAndStaffProfile.objects.all()
        
        # Optional filter by query param
        employee_type = request.query_params.get("employee_type")
        if employee_type:
            qs = qs.filter(employee_type=employee_type)

        total = qs.count()
        teachers = qs.filter(employee_type="teacher").count()
        staff = qs.filter(employee_type="staff").count()
        active = qs.filter(status="active").count()
        inactive = qs.filter(status="inactive").count()
        on_leave = qs.filter(status="on_leave").count()

        return Response({
            "total": total,
            "teachers": teachers,
            "staff": staff,
            "active": active,
            "inactive": inactive,
            "on_leave": on_leave,
        })


class EmployeeUserDropdownView(generics.ListAPIView):
    """
    Simple Dropdown/List view to populate User options with role 'Teacher' or 'Staff'
    who do not have a linked profile yet.
    """
    serializer_class = EmployeeUserDropdownSerializer
    pagination_class = None

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return User.objects.none()
            
        return User.objects.filter(
            role__name__in=['Teacher', 'Staff', 'teacher', 'staff'],
            teacher_staff_profile__isnull=True
        )
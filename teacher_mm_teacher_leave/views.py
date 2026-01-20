from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.utils import timezone
from django.db.models import Sum, Count, Q
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import LeaveType, LeaveBalance, TeacherLeave
from .serializers import (
    LeaveTypeSerializer,
    LeaveTypeCreateSerializer,
    LeaveBalanceSerializer,
    LeaveBalanceSummarySerializer,
    TeacherLeaveListSerializer,
    TeacherLeaveDetailSerializer,
    TeacherLeaveCreateSerializer,
    TeacherLeaveUpdateSerializer,
    LeaveApprovalSerializer,
    TeacherLeaveSummarySerializer,
)
from .filters import TeacherLeaveFilter
from .pagination import LeaveResultsPagination
from teacher_mm_teacher.models import Teacher

# Common Swagger tag for all teacher-related APIs
SWAGGER_TAG = ["Teachers"]


# ─────────────────────────────────────────────────────────────────────────────
# Leave Type Management
# ─────────────────────────────────────────────────────────────────────────────

class LeaveTypeViewSet(viewsets.ModelViewSet):
    """
    API for managing Leave Types.
    
    Endpoints:
    - GET /teacher/leave-types/ - List all leave types
    - POST /teacher/leave-types/ - Create a new leave type
    - GET /teacher/leave-types/{id}/ - Get leave type details
    - PUT /teacher/leave-types/{id}/ - Update leave type
    - DELETE /teacher/leave-types/{id}/ - Delete leave type
    """
    queryset = LeaveType.objects.all()
    permission_classes = [AllowAny]  # Change to IsAuthenticated in production
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "default_days", "created_at"]
    ordering = ["name"]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return LeaveTypeCreateSerializer
        return LeaveTypeSerializer

    @swagger_auto_schema(
        operation_summary="List all leave types",
        operation_description="Get all available leave types (Medical, Casual, Maternity, Paternity, etc.).",
        tags=SWAGGER_TAG
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a new leave type",
        operation_description="Create a new leave type (e.g., Medical, Casual, Maternity, Paternity).",
        tags=SWAGGER_TAG
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get leave type details",
        operation_description="Get details of a specific leave type.",
        tags=SWAGGER_TAG
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update leave type",
        operation_description="Update a leave type.",
        tags=SWAGGER_TAG
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete leave type",
        operation_description="Delete a leave type.",
        tags=SWAGGER_TAG
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


# ─────────────────────────────────────────────────────────────────────────────
# Teacher Leave Management
# ─────────────────────────────────────────────────────────────────────────────

class TeacherLeaveViewSet(viewsets.ModelViewSet):
    """
    API for managing Teacher Leave Applications.
    
    Endpoints:
    - GET /teacher/leaves/ - List all leave applications
    - POST /teacher/leaves/ - Create leave application
    - GET /teacher/leaves/{id}/ - Get leave details
    - PUT /teacher/leaves/{id}/ - Update leave
    - DELETE /teacher/leaves/{id}/ - Delete leave
    - POST /teacher/leaves/{id}/approve/ - Approve/Decline leave
    - GET /teacher/leaves/by-teacher/{teacher_id}/ - Get leaves by teacher
    - GET /teacher/leaves/summary/{teacher_id}/ - Get teacher leave summary
    """
    queryset = TeacherLeave.objects.select_related(
        "teacher", "teacher__user", "leave_type", "reviewed_by"
    ).all()
    permission_classes = [AllowAny]  # Change to IsAuthenticated in production
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = TeacherLeaveFilter
    search_fields = ["teacher__teacher_id", "teacher__user__name", "reason"]
    ordering_fields = ["applied_on", "from_date", "to_date", "status", "no_of_days"]
    ordering = ["-applied_on"]
    pagination_class = LeaveResultsPagination

    def get_serializer_class(self):
        if self.action == "create":
            return TeacherLeaveCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return TeacherLeaveUpdateSerializer
        elif self.action == "retrieve":
            return TeacherLeaveDetailSerializer
        elif self.action == "approve":
            return LeaveApprovalSerializer
        return TeacherLeaveListSerializer

    @swagger_auto_schema(
        operation_summary="List all teacher leave applications",
        operation_description="Get all leave applications with filtering and pagination.",
        tags=SWAGGER_TAG
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create leave application",
        operation_description="Create a leave application for a teacher.",
        tags=SWAGGER_TAG
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get leave application details",
        operation_description="Get full details of a leave application.",
        tags=SWAGGER_TAG
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update leave application",
        operation_description="Update a pending leave application.",
        tags=SWAGGER_TAG
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete leave application",
        operation_description="Delete a leave application.",
        tags=SWAGGER_TAG
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Approve or Decline leave",
        operation_description="""
        Approve or decline a pending leave application.
        
        Send `action` as either "approve" or "decline".
        Optionally include `admin_remarks` for feedback.
        """,
        tags=SWAGGER_TAG,
        request_body=LeaveApprovalSerializer,
        responses={
            200: TeacherLeaveDetailSerializer,
            400: "Bad Request - Invalid action or leave already processed"
        }
    )
    @action(detail=True, methods=["post"])
    def approve(self, request, pk=None):
        """Approve or decline a leave application."""
        leave = self.get_object()
        serializer = LeaveApprovalSerializer(
            data=request.data,
            context={"leave": leave}
        )
        serializer.is_valid(raise_exception=True)
        
        # Use request.user if authenticated, otherwise None
        user = request.user if request.user.is_authenticated else None
        updated_leave = serializer.save(leave=leave, user=user)
        
        return Response(
            TeacherLeaveDetailSerializer(updated_leave).data,
            status=status.HTTP_200_OK
        )

    @swagger_auto_schema(
        operation_summary="Get leaves by teacher",
        operation_description="Get all leave applications for a specific teacher.",
        tags=SWAGGER_TAG
    )
    @action(detail=False, methods=["get"], url_path="by-teacher/(?P<teacher_id>[^/.]+)")
    def by_teacher(self, request, teacher_id=None):
        """Get all leaves for a specific teacher."""
        leaves = self.queryset.filter(teacher_id=teacher_id)
        page = self.paginate_queryset(leaves)
        if page is not None:
            serializer = TeacherLeaveListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = TeacherLeaveListSerializer(leaves, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Get teacher leave summary",
        operation_description="""
        Get complete leave summary for a teacher.
        Includes leave balance cards and recent leave history.
        This is used in the teacher details page.
        """,
        tags=SWAGGER_TAG
    )
    @action(detail=False, methods=["get"], url_path="summary/(?P<teacher_id>[^/.]+)")
    def summary(self, request, teacher_id=None):
        """Get complete leave summary for a teacher including balance and history."""
        try:
            teacher = Teacher.objects.get(pk=teacher_id)
        except Teacher.DoesNotExist:
            return Response(
                {"error": "Teacher not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        year = request.query_params.get("year", timezone.now().year)

        # Get leave balances for this teacher
        leave_types = LeaveType.objects.filter(is_active=True)
        leave_balances = []

        for leave_type in leave_types:
            balance = LeaveBalance.objects.filter(
                teacher=teacher,
                leave_type=leave_type,
                year=year
            ).first()

            if balance:
                leave_balances.append({
                    "leave_type_id": leave_type.id,
                    "leave_type_name": leave_type.name,
                    "total_allocated": balance.total_allocated,
                    "used": balance.used,
                    "available": balance.available,
                })
            else:
                # No balance record, use defaults
                leave_balances.append({
                    "leave_type_id": leave_type.id,
                    "leave_type_name": leave_type.name,
                    "total_allocated": leave_type.default_days,
                    "used": 0,
                    "available": leave_type.default_days,
                })

        # Get recent leaves
        recent_leaves = TeacherLeave.objects.filter(
            teacher=teacher
        ).select_related("leave_type").order_by("-applied_on")[:10]

        # Calculate statistics
        stats = TeacherLeave.objects.filter(teacher=teacher).aggregate(
            total_leaves_taken=Count("id", filter=Q(status="approved")),
            pending_applications=Count("id", filter=Q(status="pending"))
        )

        response_data = {
            "leave_balances": leave_balances,
            "recent_leaves": TeacherLeaveListSerializer(recent_leaves, many=True).data,
            "total_leaves_taken": stats["total_leaves_taken"] or 0,
            "pending_applications": stats["pending_applications"] or 0,
        }

        return Response(response_data)

    @swagger_auto_schema(
        operation_summary="Get leave statistics",
        operation_description="Get overall leave statistics.",
        tags=SWAGGER_TAG
    )
    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Get overall leave statistics."""
        today = timezone.now().date()
        current_year = today.year

        stats = {
            "total_applications": TeacherLeave.objects.count(),
            "pending_applications": TeacherLeave.objects.filter(status="pending").count(),
            "approved_this_year": TeacherLeave.objects.filter(
                status="approved",
                from_date__year=current_year
            ).count(),
            "declined_this_year": TeacherLeave.objects.filter(
                status="declined",
                from_date__year=current_year
            ).count(),
            "teachers_on_leave_today": TeacherLeave.objects.filter(
                status="approved",
                from_date__lte=today,
                to_date__gte=today
            ).count(),
            "by_leave_type": list(
                TeacherLeave.objects.filter(status="approved", from_date__year=current_year)
                .values("leave_type__name")
                .annotate(count=Count("id"))
                .order_by("-count")
            ),
        }

        return Response(stats)


# ─────────────────────────────────────────────────────────────────────────────
# Leave Balance Management
# ─────────────────────────────────────────────────────────────────────────────

class LeaveBalanceViewSet(viewsets.ModelViewSet):
    """
    API for managing Teacher Leave Balances.
    
    Endpoints:
    - GET /teacher/leave-balances/ - List all leave balances
    - POST /teacher/leave-balances/ - Create/allocate leave balance
    - PUT /teacher/leave-balances/{id}/ - Update leave balance
    - GET /teacher/leave-balances/by-teacher/{teacher_id}/ - Get balances by teacher
    """
    queryset = LeaveBalance.objects.select_related(
        "teacher", "teacher__user", "leave_type"
    ).all()
    serializer_class = LeaveBalanceSerializer
    permission_classes = [AllowAny]  # Change to IsAuthenticated in production
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["teacher", "leave_type", "year"]
    ordering_fields = ["year", "leave_type__name", "total_allocated", "used"]
    ordering = ["-year", "leave_type__name"]

    @swagger_auto_schema(
        operation_summary="List all leave balances",
        operation_description="Get all teacher leave balances.",
        tags=SWAGGER_TAG
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Allocate leave balance",
        operation_description="Create/allocate leave balance for a teacher.",
        tags=SWAGGER_TAG
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update leave balance",
        operation_description="Update a teacher's leave balance.",
        tags=SWAGGER_TAG
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Get leave balances by teacher",
        operation_description="Get all leave balances for a specific teacher.",
        tags=SWAGGER_TAG
    )
    @action(detail=False, methods=["get"], url_path="by-teacher/(?P<teacher_id>[^/.]+)")
    def by_teacher(self, request, teacher_id=None):
        """Get all leave balances for a specific teacher."""
        year = request.query_params.get("year", timezone.now().year)
        balances = self.queryset.filter(teacher_id=teacher_id, year=year)
        serializer = self.get_serializer(balances, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="Initialize leave balances",
        operation_description="""
        Initialize leave balances for a teacher.
        Creates balance records for all active leave types with default allocations.
        """,
        tags=SWAGGER_TAG
    )
    @action(detail=False, methods=["post"], url_path="initialize/(?P<teacher_id>[^/.]+)")
    def initialize(self, request, teacher_id=None):
        """Initialize leave balances for a teacher with all active leave types."""
        try:
            teacher = Teacher.objects.get(pk=teacher_id)
        except Teacher.DoesNotExist:
            return Response(
                {"error": "Teacher not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        year = request.data.get("year", timezone.now().year)
        leave_types = LeaveType.objects.filter(is_active=True)
        created_balances = []

        for leave_type in leave_types:
            balance, created = LeaveBalance.objects.get_or_create(
                teacher=teacher,
                leave_type=leave_type,
                year=year,
                defaults={"total_allocated": leave_type.default_days}
            )
            if created:
                created_balances.append(balance)

        serializer = LeaveBalanceSerializer(created_balances, many=True)
        return Response({
            "message": f"Initialized {len(created_balances)} leave balance(s) for teacher.",
            "balances": serializer.data
        }, status=status.HTTP_201_CREATED)


# Keep old class names as aliases for backward compatibility
AdminLeaveTypeViewSet = LeaveTypeViewSet
AdminTeacherLeaveViewSet = TeacherLeaveViewSet
AdminLeaveBalanceViewSet = LeaveBalanceViewSet

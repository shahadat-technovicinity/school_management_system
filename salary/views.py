"""
Salary Management Views

Complete API endpoints for:
- Dashboard metrics
- Salary CRUD operations
- Payment processing
- Export functionality
"""

import csv
from io import StringIO
from datetime import datetime, date
from decimal import Decimal

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.db.models import Sum, Prefetch
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import EmployeeSalary, SalaryAllowance, SalaryDeduction
from .serializers import (
    SalaryListSerializer,
    SalaryDetailSerializer,
    SalaryCreateSerializer,
    SalaryUpdateSerializer,
    SalaryPaymentSerializer,
    SalaryDashboardSerializer,
    SalaryExportSerializer,
    BulkPaymentSerializer,
)
from .filters import SalaryFilter
from .pagination import SalaryPagination
from .services import SalaryDashboardService, SalaryExportService

# Common Swagger tag
SWAGGER_TAG = ["Teachers"]


# ─────────────────────────────────────────────────────────────────────────────
# Salary Dashboard View
# ─────────────────────────────────────────────────────────────────────────────

class SalaryDashboardView(APIView):
    """
    API endpoint for salary dashboard metrics.
    
    GET /salary/dashboard/
    
    Returns aggregated metrics including:
    - Total salary disbursement
    - Employee count
    - Average salary
    - Pending approvals
    - All with percentage change from previous month
    """
    permission_classes = [AllowAny]  # Change to IsAuthenticated in production

    @swagger_auto_schema(
        operation_summary="Get salary dashboard metrics",
        operation_description="""
        Get aggregated salary metrics for the dashboard.
        
        Returns:
        - Total salary disbursement for the month
        - Total employees with salary records
        - Average salary
        - Pending approvals count
        - Percentage changes from previous month
        """,
        tags=SWAGGER_TAG,
        manual_parameters=[
            openapi.Parameter(
                "month", openapi.IN_QUERY,
                description="Month in YYYY-MM format (defaults to current month)",
                type=openapi.TYPE_STRING,
                example="2025-05"
            ),
            openapi.Parameter(
                "department", openapi.IN_QUERY,
                description="Filter by department",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                "staff_category", openapi.IN_QUERY,
                description="Filter by staff category",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                "employment_type", openapi.IN_QUERY,
                description="Filter by employment type (full-time, part-time, contract)",
                type=openapi.TYPE_STRING
            ),
        ],
        responses={
            200: SalaryDashboardSerializer
        }
    )
    def get(self, request):
        # Parse month parameter
        month_str = request.query_params.get("month")
        month = None
        if month_str:
            try:
                year, month_num = month_str.split("-")
                month = date(int(year), int(month_num), 1)
            except (ValueError, AttributeError):
                pass

        # Get other filters
        department = request.query_params.get("department")
        staff_category = request.query_params.get("staff_category")
        employment_type = request.query_params.get("employment_type")

        # Calculate metrics
        service = SalaryDashboardService()
        metrics = service.get_dashboard_metrics(
            month=month,
            department=department,
            staff_category=staff_category,
            employment_type=employment_type
        )

        serializer = SalaryDashboardSerializer(metrics)
        return Response({
            "status": "success",
            "data": serializer.data
        })


# ─────────────────────────────────────────────────────────────────────────────
# Salary ViewSet
# ─────────────────────────────────────────────────────────────────────────────

class SalaryViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing employee salaries.
    
    Endpoints:
    - GET /salary/ - List all salaries (paginated, filterable)
    - POST /salary/ - Create new salary record
    - GET /salary/{id}/ - Get salary details
    - PUT /salary/{id}/ - Update salary
    - DELETE /salary/{id}/ - Delete salary
    - POST /salary/{id}/pay/ - Process payment
    - GET /salary/export/ - Export salaries to CSV
    - POST /salary/bulk-pay/ - Process bulk payments
    """
    permission_classes = [AllowAny]  # Change to IsAuthenticated in production
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = SalaryFilter
    search_fields = [
        "employee__user__name",
        "employee__user__email",
        "employee__teacher_id",
    ]
    ordering_fields = [
        "month",
        "basic_salary",
        "payment_status",
        "payment_date",
        "employee__user__name",
        "employee__subject",
        "created_at",
    ]
    ordering = ["-month", "-created_at"]
    pagination_class = SalaryPagination

    def get_queryset(self):
        """Optimized queryset with select_related and prefetch_related."""
        return EmployeeSalary.objects.select_related(
            "employee",
            "employee__user",
            "created_by",
            "paid_by",
        ).prefetch_related(
            Prefetch(
                "allowances",
                queryset=SalaryAllowance.objects.order_by("allowance_type", "name")
            ),
            Prefetch(
                "deductions",
                queryset=SalaryDeduction.objects.order_by("deduction_type", "name")
            ),
        ).annotate(
            _total_allowances=Sum("allowances__amount"),
            _total_deductions=Sum("deductions__amount"),
        )

    def get_serializer_class(self):
        if self.action == "create":
            return SalaryCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return SalaryUpdateSerializer
        elif self.action == "retrieve":
            return SalaryDetailSerializer
        elif self.action == "pay":
            return SalaryPaymentSerializer
        elif self.action == "bulk_pay":
            return BulkPaymentSerializer
        return SalaryListSerializer

    # ─────────────────────────────────────────────────────────────────────────
    # List
    # ─────────────────────────────────────────────────────────────────────────

    @swagger_auto_schema(
        operation_summary="List all salary records",
        operation_description="""
        Get paginated list of salary records with filtering and sorting.
        
        Filters:
        - month: YYYY-MM format
        - department: Department name
        - employment_type: full-time, part-time, contract
        - payment_status: pending, paid, processing, cancelled
        - search: Search by employee name, email, or ID
        """,
        tags=SWAGGER_TAG,
        manual_parameters=[
            openapi.Parameter(
                "month", openapi.IN_QUERY,
                description="Filter by month (YYYY-MM)",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                "department", openapi.IN_QUERY,
                description="Filter by department",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                "employment_type", openapi.IN_QUERY,
                description="Filter by employment type",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                "payment_status", openapi.IN_QUERY,
                description="Filter by payment status",
                type=openapi.TYPE_STRING,
                enum=["pending", "paid", "processing", "cancelled"]
            ),
            openapi.Parameter(
                "search", openapi.IN_QUERY,
                description="Search employees",
                type=openapi.TYPE_STRING
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    # ─────────────────────────────────────────────────────────────────────────
    # Create
    # ─────────────────────────────────────────────────────────────────────────

    @swagger_auto_schema(
        operation_summary="Create salary record",
        operation_description="""
        Create a new salary record for an employee.
        
        Supports:
        - Dynamic allowances (housing, transport, medical, custom)
        - Dynamic deductions (tax, pension, insurance, custom)
        - Automatic net salary calculation
        """,
        tags=SWAGGER_TAG,
        request_body=SalaryCreateSerializer,
        responses={
            201: SalaryDetailSerializer
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        salary = serializer.save()

        # Return full details
        detail_serializer = SalaryDetailSerializer(salary)
        return Response({
            "status": "success",
            "message": "Salary record created successfully",
            "data": detail_serializer.data
        }, status=status.HTTP_201_CREATED)

    # ─────────────────────────────────────────────────────────────────────────
    # Retrieve
    # ─────────────────────────────────────────────────────────────────────────

    @swagger_auto_schema(
        operation_summary="Get salary details",
        operation_description="""
        Get full details of a salary record including:
        - Employee information
        - Salary breakdown (basic, allowances, deductions)
        - Payment history (last 6 months)
        """,
        tags=SWAGGER_TAG,
        responses={
            200: SalaryDetailSerializer
        }
    )
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "status": "success",
            "data": serializer.data
        })

    # ─────────────────────────────────────────────────────────────────────────
    # Update
    # ─────────────────────────────────────────────────────────────────────────

    @swagger_auto_schema(
        operation_summary="Update salary record",
        operation_description="""
        Update a salary record including:
        - Basic salary
        - Allowances (replaces all existing)
        - Deductions (replaces all existing)
        - Payment method
        - Comments
        """,
        tags=SWAGGER_TAG,
        request_body=SalaryUpdateSerializer,
        responses={
            200: SalaryDetailSerializer
        }
    )
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        salary = serializer.save()

        # Return full details
        detail_serializer = SalaryDetailSerializer(salary)
        return Response({
            "status": "success",
            "message": "Salary record updated successfully",
            "data": detail_serializer.data
        })

    # ─────────────────────────────────────────────────────────────────────────
    # Delete
    # ─────────────────────────────────────────────────────────────────────────

    @swagger_auto_schema(
        operation_summary="Delete salary record",
        operation_description="Delete a salary record. Cannot delete paid salaries.",
        tags=SWAGGER_TAG
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.payment_status == "paid":
            return Response({
                "status": "error",
                "message": "Cannot delete a paid salary record"
            }, status=status.HTTP_400_BAD_REQUEST)

        instance.delete()
        return Response({
            "status": "success",
            "message": "Salary record deleted successfully"
        }, status=status.HTTP_204_NO_CONTENT)

    # ─────────────────────────────────────────────────────────────────────────
    # Payment Action
    # ─────────────────────────────────────────────────────────────────────────

    @swagger_auto_schema(
        operation_summary="Process salary payment",
        operation_description="""
        Mark a salary as paid or cancelled.
        
        Actions:
        - pay: Mark as paid and set payment_date
        - cancel: Mark as cancelled
        """,
        tags=SWAGGER_TAG,
        request_body=SalaryPaymentSerializer,
        responses={
            200: SalaryDetailSerializer
        }
    )
    @action(detail=True, methods=["post"])
    def pay(self, request, pk=None):
        """Process salary payment."""
        salary = self.get_object()
        serializer = SalaryPaymentSerializer(
            data=request.data,
            context={"salary": salary}
        )
        serializer.is_valid(raise_exception=True)

        user = request.user if request.user.is_authenticated else None
        updated_salary = serializer.save(salary=salary, user=user)

        detail_serializer = SalaryDetailSerializer(updated_salary)
        return Response({
            "status": "success",
            "message": f"Salary {serializer.validated_data['action']}ed successfully",
            "data": detail_serializer.data
        })

    # ─────────────────────────────────────────────────────────────────────────
    # Bulk Payment
    # ─────────────────────────────────────────────────────────────────────────

    @swagger_auto_schema(
        operation_summary="Process bulk salary payments",
        operation_description="""
        Process payments for multiple salaries at once.
        
        Send a list of salary IDs to mark as paid.
        """,
        tags=SWAGGER_TAG,
        request_body=BulkPaymentSerializer,
        responses={
            200: openapi.Response(
                description="Bulk payment result",
                examples={
                    "application/json": {
                        "status": "success",
                        "message": "Processed 5 of 5 salary payments",
                        "processed": 5,
                        "total_requested": 5
                    }
                }
            )
        }
    )
    @action(detail=False, methods=["post"], url_path="bulk-pay")
    def bulk_pay(self, request):
        """Process bulk salary payments."""
        serializer = BulkPaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user if request.user.is_authenticated else None
        result = serializer.save(user=user)

        return Response({
            "status": "success",
            "message": f"Processed {result['processed']} of {result['total_requested']} salary payments",
            **result
        })

    # ─────────────────────────────────────────────────────────────────────────
    # Export
    # ─────────────────────────────────────────────────────────────────────────

    @swagger_auto_schema(
        operation_summary="Export salary data to CSV",
        operation_description="""
        Export filtered salary data to CSV format.
        
        Apply the same filters as the list endpoint.
        Returns a downloadable CSV file.
        """,
        tags=SWAGGER_TAG,
        manual_parameters=[
            openapi.Parameter(
                "month", openapi.IN_QUERY,
                description="Filter by month (YYYY-MM)",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                "department", openapi.IN_QUERY,
                description="Filter by department",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                "payment_status", openapi.IN_QUERY,
                description="Filter by payment status",
                type=openapi.TYPE_STRING
            ),
        ]
    )
    @action(detail=False, methods=["get"])
    def export(self, request):
        """Export salary data to CSV."""
        # Get filtered queryset
        queryset = self.filter_queryset(self.get_queryset())

        # Prepare export data
        export_service = SalaryExportService()
        data = export_service.prepare_export_data(queryset)

        # Create CSV response
        response = HttpResponse(content_type="text/csv")
        
        # Generate filename
        month_str = request.query_params.get("month", datetime.now().strftime("%Y-%m"))
        response["Content-Disposition"] = f'attachment; filename="salaries_{month_str}.csv"'

        # Write CSV
        writer = csv.DictWriter(response, fieldnames=export_service.get_export_headers())
        writer.writeheader()
        writer.writerows(data)

        return response

    # ─────────────────────────────────────────────────────────────────────────
    # Employee Salary History
    # ─────────────────────────────────────────────────────────────────────────

    @swagger_auto_schema(
        operation_summary="Get employee salary history",
        operation_description="Get salary history for a specific employee.",
        tags=SWAGGER_TAG,
        manual_parameters=[
            openapi.Parameter(
                "employee_id", openapi.IN_PATH,
                description="Employee/Teacher ID",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
        ]
    )
    @action(detail=False, methods=["get"], url_path="by-employee/(?P<employee_id>[^/.]+)")
    def by_employee(self, request, employee_id=None):
        """Get all salary records for a specific employee."""
        salaries = self.get_queryset().filter(employee_id=employee_id)
        page = self.paginate_queryset(salaries)
        
        if page is not None:
            serializer = SalaryListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = SalaryListSerializer(salaries, many=True)
        return Response({
            "status": "success",
            "data": serializer.data
        })

    # ─────────────────────────────────────────────────────────────────────────
    # Statistics
    # ─────────────────────────────────────────────────────────────────────────

    @swagger_auto_schema(
        operation_summary="Get salary statistics",
        operation_description="Get overall salary statistics and breakdowns.",
        tags=SWAGGER_TAG,
        manual_parameters=[
            openapi.Parameter(
                "month", openapi.IN_QUERY,
                description="Month in YYYY-MM format",
                type=openapi.TYPE_STRING
            ),
        ]
    )
    @action(detail=False, methods=["get"])
    def statistics(self, request):
        """Get salary statistics."""
        month_str = request.query_params.get("month")
        month = None
        
        if month_str:
            try:
                year, month_num = month_str.split("-")
                month = date(int(year), int(month_num), 1)
            except (ValueError, AttributeError):
                month = None

        service = SalaryDashboardService()
        
        # Get department breakdown
        department_breakdown = service.get_department_breakdown(month)
        
        # Get payment status summary
        payment_summary = service.get_payment_status_summary(month)

        return Response({
            "status": "success",
            "data": {
                "by_department": department_breakdown,
                "payment_status_summary": payment_summary,
            }
        })

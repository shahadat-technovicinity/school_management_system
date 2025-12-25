"""
Salary Management Services

Business logic for salary calculations, dashboard metrics, and exports.
"""

from decimal import Decimal
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import Coalesce

from .models import EmployeeSalary, SalaryAllowance, SalaryDeduction
from userauthentication.models import User


class SalaryDashboardService:
    """
    Service class for calculating salary dashboard metrics.
    """

    def get_dashboard_metrics(
        self,
        department: str = None,
        position: str = None
    ) -> dict:
        """
        Calculate all dashboard metrics for the given filters.
        
        Args:
            department: Filter by department
            position: Filter by position
        
        Returns:
            Dictionary with all dashboard metrics
        """
        # Build base queryset with filters
        base_qs = EmployeeSalary.objects.all()
        
        if department:
            base_qs = base_qs.filter(department__icontains=department)
        if position:
            base_qs = base_qs.filter(position__icontains=position)

        # Calculate metrics
        data = self._calculate_metrics(base_qs)

        return {
            "total_salary_disbursement": data["total_disbursement"],
            "total_employees": data["total_employees"],
            "average_salary": data["average_salary"],
            "pending_approvals": data["pending_count"],
            "paid_count": data["paid_count"],
            "total_allowances": data["total_allowances"],
            "total_deductions": data["total_deductions"],
        }

    def _calculate_metrics(self, queryset) -> dict:
        """Calculate metrics for the queryset."""
        # Get basic aggregations
        basic_agg = queryset.aggregate(
            total_basic=Coalesce(Sum("basic_salary"), Decimal("0.00")),
            avg_basic=Coalesce(Avg("basic_salary"), Decimal("0.00")),
            total_count=Count("id"),
            pending_count=Count("id", filter=Q(payment_status="pending")),
            paid_count=Count("id", filter=Q(payment_status="paid")),
        )

        # Get allowances total
        allowances_total = SalaryAllowance.objects.filter(
            salary__in=queryset
        ).aggregate(
            total=Coalesce(Sum("amount"), Decimal("0.00"))
        )["total"]

        # Get deductions total
        deductions_total = SalaryDeduction.objects.filter(
            salary__in=queryset
        ).aggregate(
            total=Coalesce(Sum("amount"), Decimal("0.00"))
        )["total"]

        # Calculate net disbursement
        total_disbursement = basic_agg["total_basic"] + allowances_total - deductions_total

        # Calculate average net salary
        if basic_agg["total_count"] > 0:
            average_salary = total_disbursement / basic_agg["total_count"]
        else:
            average_salary = Decimal("0.00")

        return {
            "total_disbursement": total_disbursement,
            "total_basic": basic_agg["total_basic"],
            "average_salary": round(average_salary, 2),
            "total_employees": basic_agg["total_count"],
            "pending_count": basic_agg["pending_count"],
            "paid_count": basic_agg["paid_count"],
            "total_allowances": allowances_total,
            "total_deductions": deductions_total,
        }

    def get_department_breakdown(self) -> list:
        """Get salary breakdown by department."""
        return list(
            EmployeeSalary.objects
            .values("department")
            .annotate(
                total_salary=Sum("basic_salary"),
                employee_count=Count("id"),
                paid_count=Count("id", filter=Q(payment_status="paid")),
                pending_count=Count("id", filter=Q(payment_status="pending")),
            )
            .order_by("-total_salary")
        )

    def get_payment_status_summary(self) -> dict:
        """Get summary of payment statuses."""
        return EmployeeSalary.objects.aggregate(
            total=Count("id"),
            paid=Count("id", filter=Q(payment_status="paid")),
            pending=Count("id", filter=Q(payment_status="pending")),
            processing=Count("id", filter=Q(payment_status="processing")),
            cancelled=Count("id", filter=Q(payment_status="cancelled")),
        )


class SalaryCalculationService:
    """
    Service for salary calculations.
    """

    @staticmethod
    def calculate_net_salary(
        basic_salary: Decimal,
        allowances: list,
        deductions: list
    ) -> dict:
        """
        Calculate salary components.
        
        Args:
            basic_salary: Base salary amount
            allowances: List of allowance dicts with 'amount' key
            deductions: List of deduction dicts with 'amount' key
        
        Returns:
            Dictionary with total_allowances, total_deductions, gross, net
        """
        total_allowances = sum(
            Decimal(str(a.get("amount", 0))) for a in allowances
        )
        total_deductions = sum(
            Decimal(str(d.get("amount", 0))) for d in deductions
        )
        
        gross_salary = basic_salary + total_allowances
        net_salary = gross_salary - total_deductions

        return {
            "basic_salary": basic_salary,
            "total_allowances": total_allowances,
            "total_deductions": total_deductions,
            "gross_salary": gross_salary,
            "net_salary": net_salary,
        }

    @staticmethod
    def get_employee_salary_history(employee_id: int, limit: int = 12) -> list:
        """
        Get salary history for an employee.
        
        Args:
            employee_id: Employee/User ID
            limit: Number of records to retrieve
        
        Returns:
            List of salary records with computed values
        """
        salaries = EmployeeSalary.objects.filter(
            employee_id=employee_id
        ).select_related(
            "employee"
        ).prefetch_related(
            "allowances", "deductions"
        ).order_by("-created_at")[:limit]

        return [
            {
                "id": salary.id,
                "department": salary.department,
                "position": salary.position,
                "basic_salary": salary.basic_salary,
                "total_allowances": salary.total_allowances,
                "total_deductions": salary.total_deductions,
                "net_salary": salary.net_salary,
                "payment_status": salary.payment_status,
                "payment_date": salary.payment_date,
                "created_at": salary.created_at,
            }
            for salary in salaries
        ]


class SalaryExportService:
    """
    Service for exporting salary data.
    """

    @staticmethod
    def prepare_export_data(queryset) -> list:
        """
        Prepare salary data for export.
        
        Args:
            queryset: Filtered EmployeeSalary queryset
        
        Returns:
            List of dictionaries ready for CSV/Excel export
        """
        data = []
        
        for salary in queryset.select_related(
            "employee"
        ).prefetch_related("allowances", "deductions"):
            
            # Get allowance breakdown
            allowances_breakdown = ", ".join([
                f"{a.name}: {a.amount}" for a in salary.allowances.all()
            ])
            
            # Get deduction breakdown
            deductions_breakdown = ", ".join([
                f"{d.name}: {d.amount}" for d in salary.deductions.all()
            ])
            
            data.append({
                "Employee ID": salary.employee.username,
                "Employee Name": salary.employee.name,
                "Department": salary.department,
                "Position": salary.position,
                "Employee Role": salary.employee.get_role_display() if salary.employee.role else "",
                "Basic Salary": float(salary.basic_salary),
                "Allowances": float(salary.total_allowances),
                "Allowances Breakdown": allowances_breakdown,
                "Deductions": float(salary.total_deductions),
                "Deductions Breakdown": deductions_breakdown,
                "Net Salary": float(salary.net_salary),
                "Payment Status": salary.get_payment_status_display(),
                "Payment Method": salary.get_payment_method_display(),
                "Payment Date": salary.payment_date.strftime("%Y-%m-%d %H:%M") if salary.payment_date else "",
                "Created At": salary.created_at.strftime("%Y-%m-%d %H:%M"),
            })
        
        return data

    @staticmethod
    def get_export_headers() -> list:
        """Get column headers for export."""
        return [
            "Employee ID",
            "Employee Name",
            "Department",
            "Position",
            "Employee Role",
            "Basic Salary",
            "Allowances",
            "Allowances Breakdown",
            "Deductions",
            "Deductions Breakdown",
            "Net Salary",
            "Payment Status",
            "Payment Method",
            "Payment Date",
            "Created At",
        ]

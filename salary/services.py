"""
Salary Management Services

Business logic for salary calculations, dashboard metrics, and exports.
"""

from decimal import Decimal
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from django.db.models import Sum, Count, Avg, Q, F
from django.db.models.functions import Coalesce

from .models import EmployeeSalary, SalaryAllowance, SalaryDeduction
from teacher.models import Teacher


class SalaryDashboardService:
    """
    Service class for calculating salary dashboard metrics.
    """

    @staticmethod
    def get_month_start(year: int, month: int) -> date:
        """Get first day of month."""
        return date(year, month, 1)

    @staticmethod
    def get_previous_month(current_month: date) -> date:
        """Get first day of previous month."""
        return (current_month - relativedelta(months=1)).replace(day=1)

    @staticmethod
    def calculate_percent_change(current: Decimal, previous: Decimal) -> Decimal:
        """Calculate percentage change between two values."""
        if previous == 0:
            return Decimal("100.00") if current > 0 else Decimal("0.00")
        return round(((current - previous) / previous) * 100, 2)

    def get_dashboard_metrics(
        self,
        month: date = None,
        department: str = None,
        staff_category: str = None,
        employment_type: str = None
    ) -> dict:
        """
        Calculate all dashboard metrics for the given filters.
        
        Args:
            month: Target month (defaults to current month)
            department: Filter by department (subject)
            staff_category: Filter by staff category (class_assigned)
            employment_type: Filter by employment type (contract_type)
        
        Returns:
            Dictionary with all dashboard metrics
        """
        if month is None:
            today = date.today()
            month = date(today.year, today.month, 1)
        else:
            month = month.replace(day=1)

        previous_month = self.get_previous_month(month)

        # Build base queryset with filters
        base_qs = EmployeeSalary.objects.all()
        
        if department:
            base_qs = base_qs.filter(employee__subject__icontains=department)
        if staff_category:
            base_qs = base_qs.filter(employee__class_assigned__icontains=staff_category)
        if employment_type:
            base_qs = base_qs.filter(employee__contract_type__iexact=employment_type)

        # Current month data
        current_qs = base_qs.filter(month=month)
        current_data = self._calculate_month_metrics(current_qs)

        # Previous month data
        previous_qs = base_qs.filter(month=previous_month)
        previous_data = self._calculate_month_metrics(previous_qs)

        # Calculate percentage changes
        disbursement_change = self.calculate_percent_change(
            current_data["total_disbursement"],
            previous_data["total_disbursement"]
        )
        employees_change = self.calculate_percent_change(
            Decimal(current_data["total_employees"]),
            Decimal(previous_data["total_employees"])
        )
        average_change = self.calculate_percent_change(
            current_data["average_salary"],
            previous_data["average_salary"]
        )

        return {
            "total_salary_disbursement": current_data["total_disbursement"],
            "disbursement_change_percent": disbursement_change,
            "total_employees": current_data["total_employees"],
            "employees_change_percent": employees_change,
            "average_salary": current_data["average_salary"],
            "average_change_percent": average_change,
            "pending_approvals": current_data["pending_count"],
            "paid_count": current_data["paid_count"],
            "total_allowances": current_data["total_allowances"],
            "total_deductions": current_data["total_deductions"],
            "current_month": month,
            "current_month_display": month.strftime("%B %Y"),
        }

    def _calculate_month_metrics(self, queryset) -> dict:
        """Calculate metrics for a specific month's queryset."""
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

    def get_department_breakdown(self, month: date = None) -> list:
        """Get salary breakdown by department (subject)."""
        if month is None:
            today = date.today()
            month = date(today.year, today.month, 1)

        return list(
            EmployeeSalary.objects.filter(month=month)
            .values("employee__subject")
            .annotate(
                department=F("employee__subject"),
                total_salary=Sum("basic_salary"),
                employee_count=Count("id"),
                paid_count=Count("id", filter=Q(payment_status="paid")),
                pending_count=Count("id", filter=Q(payment_status="pending")),
            )
            .order_by("-total_salary")
        )

    def get_payment_status_summary(self, month: date = None) -> dict:
        """Get summary of payment statuses."""
        if month is None:
            today = date.today()
            month = date(today.year, today.month, 1)

        return EmployeeSalary.objects.filter(month=month).aggregate(
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
    def get_employee_salary_history(employee_id: int, months: int = 12) -> list:
        """
        Get salary history for an employee.
        
        Args:
            employee_id: Employee/Teacher ID
            months: Number of months to retrieve
        
        Returns:
            List of salary records with computed values
        """
        salaries = EmployeeSalary.objects.filter(
            employee_id=employee_id
        ).select_related(
            "employee", "employee__user"
        ).prefetch_related(
            "allowances", "deductions"
        ).order_by("-month")[:months]

        return [
            {
                "id": salary.id,
                "month": salary.month,
                "month_display": salary.month.strftime("%B %Y"),
                "basic_salary": salary.basic_salary,
                "total_allowances": salary.total_allowances,
                "total_deductions": salary.total_deductions,
                "net_salary": salary.net_salary,
                "payment_status": salary.payment_status,
                "payment_date": salary.payment_date,
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
            "employee", "employee__user"
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
                "Employee ID": salary.employee.teacher_id,
                "Employee Name": salary.employee.user.name,
                "Department": salary.employee.subject or "",
                "Position": salary.employee.qualification or "",
                "Employment Type": salary.employee.get_contract_type_display() if salary.employee.contract_type else "",
                "Month": salary.month.strftime("%B %Y"),
                "Basic Salary": float(salary.basic_salary),
                "Allowances": float(salary.total_allowances),
                "Allowances Breakdown": allowances_breakdown,
                "Deductions": float(salary.total_deductions),
                "Deductions Breakdown": deductions_breakdown,
                "Net Salary": float(salary.net_salary),
                "Payment Status": salary.get_payment_status_display(),
                "Payment Method": salary.get_payment_method_display(),
                "Payment Date": salary.payment_date.strftime("%Y-%m-%d %H:%M") if salary.payment_date else "",
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
            "Employment Type",
            "Month",
            "Basic Salary",
            "Allowances",
            "Allowances Breakdown",
            "Deductions",
            "Deductions Breakdown",
            "Net Salary",
            "Payment Status",
            "Payment Method",
            "Payment Date",
        ]

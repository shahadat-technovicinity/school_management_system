from rest_framework import generics
from rest_framework.response import Response
from django.db.models import Sum
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from account_mm_collect_fee.models import FeeCollection
from teacher_mm_add_salary.models import SalaryRecord
from account_mm_income.models import account_Income
from account_mm_expence.models import Expense
from .serializers import (
    FeeCollectionReportSerializer,
    SalaryDisbursementReportSerializer,
    FinancialSummarySerializer,
)


class FeeCollectionReportView(generics.GenericAPIView):
    serializer_class = FeeCollectionReportSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('class_name', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('from_date', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False),
            openapi.Parameter('to_date', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False),
        ]
    )
    def get(self, request, *args, **kwargs):
        class_name = request.query_params.get('class_name')
        from_date = request.query_params.get('from_date')
        to_date = request.query_params.get('to_date')

        queryset = FeeCollection.objects.all()

        if class_name:
            queryset = queryset.filter(student__class_name_static=class_name)
        if from_date:
            queryset = queryset.filter(payment_date__gte=from_date)
        if to_date:
            queryset = queryset.filter(payment_date__lte=to_date)

        total_collected = queryset.filter(status='paid').aggregate(
            total=Sum('final_amount')
        )['total'] or 0

        pending = queryset.filter(status='due').aggregate(
            total=Sum('final_amount')
        )['total'] or 0

        total = float(total_collected) + float(pending)
        collection_rate = round((float(total_collected) / total) * 100, 1) if total else 0

        students = []
        for col in queryset.select_related('student').prefetch_related('items'):
            for item in col.items.all():
                students.append({
                    'receipt_id': f'RC-{col.id:04d}',
                    'student_id': col.student.admission_number,
                    'name': col.student.full_name,
                    'class': col.student.class_name_static,
                    'fee_type': item.fee.fee_type,
                    'amount': float(item.amount),
                    'due_date': item.fee.due_date,
                    'payment_date': col.payment_date,
                    'payment_method': col.payment_method,
                    'status': col.status,
                })

        return Response({
            'stats': {
                'total_collected': total_collected,
                'pending': pending,
                'collection_rate': collection_rate,
            },
            'collections': students,
        })


class SalaryDisbursementReportView(generics.GenericAPIView):
    serializer_class = SalaryDisbursementReportSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('month', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('year', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('department', openapi.IN_QUERY, type=openapi.TYPE_STRING, required=False),
        ]
    )
    def get(self, request, *args, **kwargs):
        month = request.query_params.get('month')
        year = request.query_params.get('year')
        department = request.query_params.get('department')

        queryset = SalaryRecord.objects.all().prefetch_related(
            'allowances', 'deductions', 'extra_works'
        ).select_related('employee')

        if month:
            queryset = queryset.filter(created_at__month=month)
        if year:
            queryset = queryset.filter(created_at__year=year)
        if department:
            queryset = queryset.filter(department=department)

        total_staff = queryset.count()
        paid = queryset.filter(status='Paid').count()
        disbursement_rate = round((paid / total_staff) * 100, 1) if total_staff else 0

        total_salary = 0
        staff_list = []

        for record in queryset:
            allowances = sum(a.amount for a in record.allowances.all() if a.amount)
            extra = sum(e.hours * e.rate_per_hour for e in record.extra_works.all())
            deductions = sum(d.amount for d in record.deductions.all() if d.amount)
            net_salary = record.basic_salary + allowances + extra - deductions
            total_salary += float(net_salary)

            staff_list.append({
                'id': record.employee.id,
                'name': record.employee.name,
                'designation': record.position,
                'department': record.department,
                'basic_salary': float(record.basic_salary),
                'allowances': float(allowances + extra),
                'deductions': float(deductions),
                'net_salary': float(net_salary),
                'status': record.status,
            })

        average_salary = round(total_salary / total_staff, 2) if total_staff else 0

        return Response({
            'stats': {
                'total_salary': total_salary,
                'total_staff': total_staff,
                'average_salary': average_salary,
                'disbursement_rate': disbursement_rate,
            },
            'staff': staff_list,
        })


class FinancialSummaryReportView(generics.GenericAPIView):
    serializer_class = FinancialSummarySerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('year', openapi.IN_QUERY, type=openapi.TYPE_INTEGER, required=False),
        ]
    )
    def get(self, request, *args, **kwargs):
        year = request.query_params.get('year', timezone.now().year)

        monthly_data = []
        for month in range(1, 13):
            fee_income = FeeCollection.objects.filter(
                status='paid',
                payment_date__year=year,
                payment_date__month=month,
            ).aggregate(total=Sum('final_amount'))['total'] or 0

            other_income = account_Income.objects.filter(
                date__year=year,
                date__month=month,
            ).aggregate(total=Sum('amount'))['total'] or 0

            total_income = float(fee_income) + float(other_income)

            salary_expense = 0
            salary_records = SalaryRecord.objects.filter(
                status='Paid',
                created_at__year=year,
                created_at__month=month,
            ).prefetch_related('allowances', 'deductions', 'extra_works')

            for record in salary_records:
                allowances = sum(a.amount for a in record.allowances.all() if a.amount)
                extra = sum(e.hours * e.rate_per_hour for e in record.extra_works.all())
                deductions = sum(d.amount for d in record.deductions.all() if d.amount)
                net = record.basic_salary + allowances + extra - deductions
                salary_expense += float(net)

            other_expense = float(Expense.objects.filter(
                expense_date__year=year,
                expense_date__month=month,
            ).aggregate(total=Sum('amount'))['total'] or 0)

            total_expense = salary_expense + other_expense
            net_balance = total_income - total_expense

            monthly_data.append({
                'month': f'{year}-{month:02d}',
                'total_income': total_income,
                'fee_collection': float(fee_income),
                'other_income': float(other_income),
                'total_expense': total_expense,
                'total_salary': salary_expense,
                'other_expense': other_expense,
                'net_balance': net_balance,
            })

        total_income = sum(m['total_income'] for m in monthly_data)
        total_fee_collection = sum(m['fee_collection'] for m in monthly_data)
        total_expense = sum(m['total_expense'] for m in monthly_data)
        net_balance = total_income - total_expense

        return Response({
            'stats': {
                'total_income': total_income,
                'total_fee_collection': total_fee_collection,
                'net_expense': total_expense,
                'net_balance': net_balance,
                'profit_margin': round((net_balance / total_income) * 100, 1) if total_income else 0,
            },
            'monthly_summary': monthly_data,
        })
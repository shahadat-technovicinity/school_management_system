from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.contrib.auth import get_user_model
from datetime import date
from .models import SalaryRecord, PaymentHistory
from .serializers import SalaryRecordSerializer, EmployeeListSerializer
import json

User = get_user_model()


class EmployeeListView(generics.ListAPIView):
    serializer_class = EmployeeListSerializer

    def get_queryset(self):
        return User.objects.filter(role__name__in=['Teacher', 'Staff'])


class SalaryListCreateView(generics.ListCreateAPIView):
    serializer_class = SalaryRecordSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        queryset = SalaryRecord.objects.all().prefetch_related(
            'allowances', 'deductions', 'extra_works', 'payment_history'
        ).select_related('employee').order_by('-created_at')

        department = self.request.query_params.get('department')
        status_filter = self.request.query_params.get('status')
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')

        if department:
            queryset = queryset.filter(department=department)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if month:
            queryset = queryset.filter(created_at__month=month)
        if year:
            queryset = queryset.filter(created_at__year=year)

        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data.copy()

        if isinstance(data.get('allowances'), str):
            data['allowances'] = json.loads(data.get('allowances', '[]'))
        if isinstance(data.get('deductions'), str):
            data['deductions'] = json.loads(data.get('deductions', '[]'))
        if isinstance(data.get('extra_works'), str):
            data['extra_works'] = json.loads(data.get('extra_works', '[]'))

        if not data.get('allowances'):
            allowances = []
            i = 0
            while f'allowances[{i}][name]' in data:
                allowances.append({
                    'name': data.get(f'allowances[{i}][name]'),
                    'amount': data.get(f'allowances[{i}][amount]'),
                })
                i += 1
            data['allowances'] = allowances

        if not data.get('deductions'):
            deductions = []
            i = 0
            while f'deductions[{i}][name]' in data:
                deductions.append({
                    'name': data.get(f'deductions[{i}][name]'),
                    'amount': data.get(f'deductions[{i}][amount]'),
                })
                i += 1
            data['deductions'] = deductions

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SalaryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SalaryRecord.objects.all().prefetch_related(
        'allowances', 'deductions', 'extra_works', 'payment_history'
    ).select_related('employee')
    serializer_class = SalaryRecordSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def update(self, request, *args, **kwargs):
        data = request.data.copy()

        if isinstance(data.get('allowances'), str):
            data['allowances'] = json.loads(data.get('allowances', '[]'))
        if isinstance(data.get('deductions'), str):
            data['deductions'] = json.loads(data.get('deductions', '[]'))
        if isinstance(data.get('extra_works'), str):
            data['extra_works'] = json.loads(data.get('extra_works', '[]'))

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


class SalaryApproveView(APIView):
    def patch(self, request, pk):
        try:
            salary = SalaryRecord.objects.prefetch_related(
                'allowances', 'deductions', 'extra_works'
            ).get(pk=pk)

            allowances = sum(a.amount for a in salary.allowances.all() if a.amount)
            extra = sum(e.hours * e.rate_per_hour for e in salary.extra_works.all())
            deductions = sum(d.amount for d in salary.deductions.all() if d.amount)
            net_salary = salary.basic_salary + allowances + extra - deductions

            salary.status = 'Paid'
            salary.save()

            today = date.today()
            PaymentHistory.objects.create(
                salary_record=salary,
                month=today.strftime('%B'),
                year=today.year,
                net_salary=net_salary,
                status='Paid',
                payment_date=today,
            )

            return Response({'message': 'Salary approved and marked as Paid'}, status=status.HTTP_200_OK)
        except SalaryRecord.DoesNotExist:
            return Response({'error': 'Salary record not found'}, status=status.HTTP_404_NOT_FOUND)


class SalaryStatsView(APIView):
    def get(self, request):
        records = SalaryRecord.objects.prefetch_related('allowances', 'deductions', 'extra_works')

        total_employees = records.values('employee').distinct().count()
        pending_approvals = records.filter(status='Pending').count()

        total_disbursement = 0
        total_salary_sum = 0
        count = 0

        for record in records:
            allowances = sum(a.amount for a in record.allowances.all() if a.amount)
            extra = sum(e.hours * e.rate_per_hour for e in record.extra_works.all())
            deductions = sum(d.amount for d in record.deductions.all() if d.amount)
            net = record.basic_salary + allowances + extra - deductions
            total_salary_sum += net
            count += 1
            if record.status == 'Paid':
                total_disbursement += net

        average_salary = round(total_salary_sum / count, 2) if count > 0 else 0

        return Response({
            'total_disbursement': total_disbursement,
            'total_employees': total_employees,
            'average_salary': average_salary,
            'pending_approvals': pending_approvals,
        })
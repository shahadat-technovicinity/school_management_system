from rest_framework import generics
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum
from account_mm_income.models import account_Income
from account_mm_expence.models import Expense
from account_mm_collect_fee.models import FeeCollection
from account_mm_create_fee.models import CreateFee
from .serializers import AccountStatsSerializer
from apps.attendance.models import Attendance
from apps.students.models import Student


class AccountStatsView(generics.GenericAPIView):
    serializer_class = AccountStatsSerializer

    def get(self, request, *args, **kwargs):
        today = timezone.now().date()

        # Today's Income — other income + fee collection
        other_income = float(account_Income.objects.filter(
            date=today
        ).aggregate(total=Sum('amount'))['total'] or 0)

        fee_income = float(FeeCollection.objects.filter(
            payment_date=today,
            status='paid'
        ).aggregate(total=Sum('final_amount'))['total'] or 0)

        todays_income = other_income + fee_income

        # Today's Expense
        todays_expense = float(Expense.objects.filter(
            expense_date=today
        ).aggregate(total=Sum('amount'))['total'] or 0)

        # Total Pending
        # Only fees where due_date >= today (not expired)
        total_assigned = float(CreateFee.objects.filter(
            due_date__gte=today
        ).aggregate(total=Sum('amount'))['total'] or 0)

        # Total paid fee
        total_paid = float(FeeCollection.objects.filter(
            status='paid'
        ).aggregate(total=Sum('final_amount'))['total'] or 0)

        # Pending = assigned - paid
        todays_pending = max(total_assigned - total_paid, 0)

        net_balance = todays_income - todays_expense

        return Response({
            'todays_income': todays_income,
            'todays_expense': todays_expense,
            'todays_pending': todays_pending,
            'net_balance': net_balance,
        })





class StudentAttendanceStatsView(generics.GenericAPIView):
    serializer_class = AccountStatsSerializer

    def get(self, request, *args, **kwargs):
        today = timezone.now().date()

        # Today's attendance
        today_attendance = Attendance.objects.filter(date=today)

        total_present = today_attendance.filter(status='P').count()
        total_absent = today_attendance.filter(status='A').count()

        total_students = Student.objects.filter(status='active').count()
        attendance_rate = round((total_present / total_students) * 100, 1) if total_students else 0

        # Male students
        male_student_ids = Student.objects.filter(
            status='active', gender='male'
        ).values_list('id', flat=True)

        male_attendance = today_attendance.filter(student_id__in=male_student_ids)
        male_present = male_attendance.filter(status='P').count()
        male_absent = male_attendance.filter(status='A').count()

        # Female students
        female_student_ids = Student.objects.filter(
            status='active', gender='female'
        ).values_list('id', flat=True)

        female_attendance = today_attendance.filter(student_id__in=female_student_ids)
        female_present = female_attendance.filter(status='P').count()
        female_absent = female_attendance.filter(status='A').count()

        return Response({
            'today': {
                'total_students': total_students,
                'present': total_present,
                'absent': total_absent,
                'on_leave': 0,
                'attendance_rate': attendance_rate,
            },
            'male_students': {
                'total': len(male_student_ids),
                'present': male_present,
                'absent': male_absent,
                'on_leave': 0,
            },
            'female_students': {
                'total': len(female_student_ids),
                'present': female_present,
                'absent': female_absent,
                'on_leave': 0,
            },
        })
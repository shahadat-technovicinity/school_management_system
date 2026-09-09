from rest_framework import generics
from rest_framework.response import Response
from datetime import date as today_date, datetime, timedelta
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.attendance.models import Attendance
from .serializers import AttendanceReportSerializer


class AttendanceReportView(generics.GenericAPIView):
    serializer_class = AttendanceReportSerializer

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('classname', openapi.IN_QUERY, description="Academic Class ID", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter('section', openapi.IN_QUERY, description="Section ID", type=openapi.TYPE_INTEGER, required=False),
            openapi.Parameter(
                'filter_type', openapi.IN_QUERY, 
                description="Report Type: all, daily, weekly, monthly, yearly", 
                type=openapi.TYPE_STRING, 
                enum=['all', 'daily', 'weekly', 'monthly', 'yearly'],
                default='all'
            ),
            openapi.Parameter('date', openapi.IN_QUERY, description="Date (YYYY-MM-DD)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('year', openapi.IN_QUERY, description="Year (e.g. 2026)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('month', openapi.IN_QUERY, description="Month number (1-12)", type=openapi.TYPE_INTEGER),
        ]
    )
    def get(self, request, *args, **kwargs):
        class_id = request.query_params.get('classname') or request.query_params.get('class_id')
        section_id = request.query_params.get('section') or request.query_params.get('section_id')
        
        filter_type = request.query_params.get('filter_type', 'all')
        report_date = request.query_params.get('date')
        year = request.query_params.get('year')
        month = request.query_params.get('month')

        # Base Queryset
        queryset = Attendance.objects.select_related('student', 'classname', 'section', 'marked_by')

        # ১. ক্লাস এবং সেকশন ফিল্টার
        if class_id:
            queryset = queryset.filter(classname_id=class_id)
        if section_id:
            queryset = queryset.filter(section_id=section_id)

        # ২. সময়ভিত্তিক ফিল্টারিং লজিক
        date_info = "All Records"

        if filter_type == 'daily':
            if report_date:
                selected_date = report_date
            else:
                # ইউজার কোনো তারিখ না দিলে ডাটাবেজের সর্বশেষ তারিখটি অটো সিলেক্ট করবে
                latest_record = queryset.order_by('-date').first()
                selected_date = str(latest_record.date) if latest_record else str(today_date.today())
            
            queryset = queryset.filter(date=selected_date)
            date_info = selected_date

        elif filter_type == 'weekly':
            ref_date = datetime.strptime(report_date, "%Y-%m-%d").date() if report_date else today_date.today()
            start_of_week = ref_date - timedelta(days=ref_date.weekday())
            end_of_week = start_of_week + timedelta(days=6)
            queryset = queryset.filter(date__range=[start_of_week, end_of_week])
            date_info = f"{start_of_week} to {end_of_week}"

        elif filter_type == 'monthly':
            current_month = int(month) if month else today_date.today().month
            if year:
                queryset = queryset.filter(date__year=int(year), date__month=current_month)
                date_info = f"{year}-{current_month:02d}"
            else:
                queryset = queryset.filter(date__month=current_month)
                date_info = f"Month-{current_month:02d}"

        elif filter_type == 'yearly':
            current_year = int(year) if year else today_date.today().year
            queryset = queryset.filter(date__year=current_year)
            date_info = str(current_year)

        # ৩. সামারি ক্যালকুলেশন
        total = queryset.count()
        present = queryset.filter(status='P').count()
        absent = queryset.filter(status='A').count()

        # ৪. স্টুডেন্ট লিস্ট তৈরি
        students = []
        for att in queryset:
            student_obj = att.student
            student_id_val = getattr(student_obj, 'admission_number', None) or getattr(student_obj, 'id', '')
            
            student_name_val = getattr(student_obj, 'student_name_english', None) or \
                               getattr(student_obj, 'full_name', None) or \
                               f"{getattr(student_obj, 'first_name', '')} {getattr(student_obj, 'last_name', '')}".strip()

            students.append({
                'attendance_date': str(att.date),
                'student_id': student_id_val,
                'name': student_name_val if student_name_val else f"Student #{student_obj.id}",
                'class': str(att.classname) if att.classname else '',
                'section': str(att.section) if att.section else '',
                'status': 'Present' if att.status == 'P' else 'Absent',
            })

        return Response({
            'filter_type': filter_type,
            'period': date_info,
            'summary': {
                'total_attendance_records': total,
                'total_present': present,
                'total_absent': absent,
                'present_percentage': round((present / total) * 100, 1) if total else 0,
                'absent_percentage': round((absent / total) * 100, 1) if total else 0,
            },
            'students': students,
        })
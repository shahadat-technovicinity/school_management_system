from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import OuterRef, Subquery
from django.utils import timezone
from django.utils.dateparse import parse_date
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from apps.attendance.models import Attendance
from apps.attendance.serializers.attendance import (
    AttendanceListSerializer, 
    AttendancePatchSerializer, 
    BulkAttendanceSerializer
)
from apps.common.pagination.standard_pagination import StandardPagination
from apps.academics.models import AcademicYear


class BulkAttendanceAPIView(CreateAPIView):
    serializer_class = BulkAttendanceSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Attendance marked successfully"}, status=201)


class AttendancePatchByKeyAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        serializer = AttendancePatchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        attendance = get_object_or_404(
            Attendance,
            student=data['student'],
            classname=data['classname'],
            section=data['section'],
            date=data['date']
        )

        attendance.status = data['status']
        if hasattr(request.user, 'teacher'):
            attendance.marked_by = request.user
        attendance.save()

        return Response({"detail": "Attendance updated successfully"})


class StudentAttendanceListAPIView(ListAPIView):
    serializer_class = AttendanceListSerializer
    pagination_class = StandardPagination

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('student_id', openapi.IN_QUERY, description="Student ID (optional)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('classname', openapi.IN_QUERY, description="Class ID (optional)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('section', openapi.IN_QUERY, description="Section ID (optional)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('date_from', openapi.IN_QUERY, description="Start date (YYYY-MM-DD)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('date_to', openapi.IN_QUERY, description="End date (YYYY-MM-DD)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('marked_by', openapi.IN_QUERY, description="Teacher User ID who marked attendance", type=openapi.TYPE_INTEGER),
            openapi.Parameter('date', openapi.IN_QUERY, description="Specific date (YYYY-MM-DD)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Order by field (prefix with - for descending)", type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Attendance.objects.none()

        queryset = Attendance.objects.select_related('student', 'classname', 'section', 'marked_by').all()

        student_id = self.kwargs.get('student_id') or self.request.query_params.get('student_id')
        class_name = self.request.query_params.get('classname')
        section = self.request.query_params.get('section')
        marked_by = self.request.query_params.get('marked_by')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        date = self.request.query_params.get('date')

        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if class_name:
            queryset = queryset.filter(classname_id=class_name)
        if section:
            queryset = queryset.filter(section_id=section)
        if marked_by:
            queryset = queryset.filter(marked_by_id=marked_by)

        # ১. নির্দিষ্ট তারিখ ফিল্টার
        if date:
            queryset = queryset.filter(date=date)
        elif date_from and date_to:
            queryset = queryset.filter(date__range=[date_from, date_to])
        elif date_from:
            queryset = queryset.filter(date__gte=date_from)
        elif date_to:
            queryset = queryset.filter(date__lte=date_to)
        else:
            # 🟢 ২. যদি তারিখ সংক্রান্ত কোনো প্যারামিটার না আসে:
            # অ্যাক্টিভ একাডেমিক ইয়ারের সাল অথবা চলতি বছর দিয়ে ফিল্টার করা
            active_year = AcademicYear.objects.filter(is_active=True).first()
            year_val = str(getattr(active_year, 'name', getattr(active_year, 'year', timezone.now().year))) if active_year else str(timezone.now().year)
            
            # শুধুমাত্র চলতি বছরের ডাটা ফিল্টার
            queryset = queryset.filter(date__year=year_val)

            # 🟢 ৩. প্রতিটি স্টুডেন্টের সর্বশেষ ১টি ডাটা ফিল্টার করা (ডুপ্লিকেট রিমুভ)
            latest_attendance_ids = Attendance.objects.filter(
                student=OuterRef('student'),
                classname_id=class_name if class_name else OuterRef('classname'),
                section_id=section if section else OuterRef('section')
            ).order_by('-date', '-id').values('id')[:1]

            queryset = queryset.filter(id__in=Subquery(latest_attendance_ids))

        ordering = self.request.query_params.get('ordering', '-date')
        if ordering:
            queryset = queryset.order_by(ordering)

        return queryset
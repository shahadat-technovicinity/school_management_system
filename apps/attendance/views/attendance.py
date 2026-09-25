from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.attendance.models import Attendance
from apps.attendance.serializers.attendance import (
    AttendanceListSerializer,
    AttendancePatchSerializer,
    BulkAttendanceSerializer,
)
from apps.common.pagination.standard_pagination import StandardPagination


class BulkAttendanceAPIView(CreateAPIView):
    serializer_class = BulkAttendanceSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Attendance marked successfully"}, status=status.HTTP_201_CREATED)


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
            openapi.Parameter('academic_year', openapi.IN_QUERY, description="Academic Year ID/Name (optional)", type=openapi.TYPE_STRING),
            openapi.Parameter('date_from', openapi.IN_QUERY, description="Start date (YYYY-MM-DD)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('date_to', openapi.IN_QUERY, description="End date (YYYY-MM-DD)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('marked_by', openapi.IN_QUERY, description="Teacher User ID who marked attendance", type=openapi.TYPE_INTEGER),
            openapi.Parameter('date', openapi.IN_QUERY, description="Specific date (YYYY-MM-DD)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Order by field (prefix with - for descending)", type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Number of items per page", type=openapi.TYPE_INTEGER),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Attendance.objects.none()

        queryset = Attendance.objects.select_related('student', 'marked_by', 'classname', 'section').all()

        student_id = self.kwargs.get('student_id') or self.request.query_params.get('student_id')
        class_name = self.request.query_params.get('classname')
        section = self.request.query_params.get('section')
        marked_by = self.request.query_params.get('marked_by')
        academic_year = self.request.query_params.get('academic_year')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        date = self.request.query_params.get('date')

        # ১. স্টুডেন্ট, ক্লাস, সেকশন ও মার্কার ফিল্টারিং
        if student_id:
            queryset = queryset.filter(student_id=student_id)
        if class_name:
            queryset = queryset.filter(classname_id=class_name)
        if section:
            queryset = queryset.filter(section_id=section)
        if marked_by:
            queryset = queryset.filter(marked_by_id=marked_by)

        # ২. Academic Year গ্লোবাল ফিল্টার
        if academic_year:
            queryset = queryset.filter(
                Q(student__academic_year__icontains=str(academic_year)) |
                Q(classname__academic_year__icontains=str(academic_year))
            )
        else:
            current_year = str(timezone.now().year)
            queryset = queryset.filter(student__academic_year__icontains=current_year)

        # ৩. তারিখ ফিল্টারিং
        if date:
            queryset = queryset.filter(date=date)
        elif date_from and date_to:
            queryset = queryset.filter(date__range=[date_from, date_to])
        elif date_from:
            queryset = queryset.filter(date__gte=date_from)
        elif date_to:
            queryset = queryset.filter(date__lte=date_to)

        return queryset.order_by('-date', '-id')

    def list(self, request, *args, **kwargs):
        # ফিল্টার হওয়া কুয়েরিসেট আনা হচ্ছে
        queryset = self.filter_queryset(self.get_queryset())

        # ওভারঅল ফিল্টারড কাউন্ট
        total_records = queryset.count()
        present_qs = queryset.filter(status='P')
        absent_qs = queryset.filter(status='A')

        total_present = present_qs.count()
        total_absent = absent_qs.count()

        # জেন্ডারভিত্তিক কাউন্ট
        male_present = present_qs.filter(
            Q(student__gender__iexact='M') | Q(student__gender__iexact='Male')
        ).count()
        
        female_present = present_qs.filter(
            Q(student__gender__iexact='F') | Q(student__gender__iexact='Female')
        ).count()

        male_absent = absent_qs.filter(
            Q(student__gender__iexact='M') | Q(student__gender__iexact='Male')
        ).count()

        female_absent = absent_qs.filter(
            Q(student__gender__iexact='F') | Q(student__gender__iexact='Female')
        ).count()

        # পেজিনেশন রেসপন্স হ্যান্ডলিং
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)

            response.data['summary'] = {
                'total_records': total_records,
                'total_present': total_present,
                'total_absent': total_absent,
                'male_present': male_present,
                'female_present': female_present,
                'male_absent': male_absent,
                'female_absent': female_absent,
            }
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'summary': {
                'total_records': total_records,
                'total_present': total_present,
                'total_absent': total_absent,
                'male_present': male_present,
                'female_present': female_present,
                'male_absent': male_absent,
                'female_absent': female_absent,
            },
            'results': serializer.data
        })
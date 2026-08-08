# attendance/views.py
from rest_framework.views import APIView
from apps.attendance.models import Attendance
from apps.attendance.serializers.attendance import AttendanceListSerializer, AttendancePatchSerializer, BulkAttendanceSerializer
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class BulkAttendanceAPIView(CreateAPIView):
    serializer_class = BulkAttendanceSerializer
    # permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


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
        attendance.marked_by = request.user.teacher
        attendance.save()

        return Response({"detail": "Attendance updated successfully"})


class StudentAttendanceListAPIView(ListAPIView):
    serializer_class = AttendanceListSerializer
    # permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('student_id', openapi.IN_PATH, description="Student ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('classname', openapi.IN_QUERY, description="Class name", type=openapi.TYPE_STRING),
            openapi.Parameter('section', openapi.IN_QUERY, description="Section", type=openapi.TYPE_STRING),
            openapi.Parameter('date_from', openapi.IN_QUERY, description="Start date (YYYY-MM-DD)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('date_to', openapi.IN_QUERY, description="End date (YYYY-MM-DD)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('marked_by', openapi.IN_QUERY, description="Teacher ID who marked attendance", type=openapi.TYPE_INTEGER),
            openapi.Parameter('date', openapi.IN_QUERY, description="Specific date (YYYY-MM-DD)", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('ordering', openapi.IN_QUERY, description="Order by field (prefix with - for descending)", type=openapi.TYPE_STRING),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Attendance.objects.none()
        
        student_id = self.kwargs.get('student_id')
        if student_id is None:
            return Attendance.objects.none()
        
        queryset = Attendance.objects.filter(student_id=student_id)

        class_name = self.request.query_params.get('classname')
        section = self.request.query_params.get('section')

        marked_by = self.request.query_params.get('marked_by')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        date = self.request.query_params.get('date')

        if class_name:
            queryset = queryset.filter(classname=class_name)

        if section:
            queryset = queryset.filter(section=section)

        if marked_by:
            queryset = queryset.filter(marked_by_id=marked_by)

        if date:
            queryset = queryset.filter(date=date)

        if date_from and date_to:
            queryset = queryset.filter(date__range=[date_from, date_to])
        elif date_from:
            queryset = queryset.filter(date__gte=date_from)
        elif date_to:
            queryset = queryset.filter(date__lte=date_to)

        ordering = self.request.query_params.get('ordering', '-date')
        if ordering:
            queryset = queryset.order_by(ordering)

        return queryset

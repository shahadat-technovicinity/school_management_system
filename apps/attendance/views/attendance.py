# attendance/views.py
from rest_framework.views import APIView
from apps.attendance.models import Attendance
from apps.attendance.serializers.attendance import AttendanceListSerializer, AttendancePatchSerializer, BulkAttendanceSerializer
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

class BulkAttendanceAPIView(CreateAPIView):
    serializer_class = BulkAttendanceSerializer
    permission_classes = [IsAuthenticated]

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



from rest_framework.generics import ListAPIView

class StudentAttendanceListAPIView(ListAPIView):
    serializer_class = AttendanceListSerializer
    # permission_classes = [IsAuthenticated]

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
        date = self.request.query_params.get('date')

        if class_name:
            queryset = queryset.filter(classname=class_name)

        if section:
            queryset = queryset.filter(section=section)

        if marked_by:
            queryset = queryset.filter(marked_by_id=marked_by)

        if date:
            queryset = queryset.filter(date=date)

        return queryset.order_by('-date')

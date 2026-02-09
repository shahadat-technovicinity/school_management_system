# attendance/views.py
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
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
            class_section=data['class_section'],
            date=data['date']
        )

        attendance.status = data['status']
        attendance.marked_by = request.user.teacher
        attendance.save()

        return Response({"detail": "Attendance updated successfully"})



from rest_framework.generics import ListAPIView

class StudentAttendanceListAPIView(ListAPIView):
    serializer_class = AttendanceListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        student_id = self.kwargs['student_id']
        queryset = Attendance.objects.filter(student_id=student_id)

        class_section = self.request.query_params.get('class_section')
        marked_by = self.request.query_params.get('marked_by')
        date = self.request.query_params.get('date')

        if class_section:
            queryset = queryset.filter(class_section_id=class_section)

        if marked_by:
            queryset = queryset.filter(marked_by_id=marked_by)

        if date:
            queryset = queryset.filter(date=date)

        return queryset.order_by('-date')

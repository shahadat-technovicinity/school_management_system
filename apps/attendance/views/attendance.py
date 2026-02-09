from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.attendance.services import bulk_mark_attendance
from apps.academics.models import ClassSection

class BulkAttendanceAPIView(APIView):
    def post(self, request):
        class_section = ClassSection.objects.get(
            id=request.data['class_section']
        )

        bulk_mark_attendance(
            class_section=class_section,
            date=request.data['date'],
            records=request.data['records'],
            teacher=request.user.teacher
        )

        return Response({"status": "ok"}, status=201)

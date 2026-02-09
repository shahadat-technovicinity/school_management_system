from apps.attendance.serializers.attendance import BulkAttendanceRequestSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from apps.attendance.services import bulk_mark_attendance
from apps.academics.models import ClassSection

class BulkAttendanceAPIView(APIView):
    def post(self, request):
        serializer = BulkAttendanceRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        class_section = ClassSection.objects.get(
            id=data["class_section"]
        )

        result = bulk_mark_attendance(
            class_section=class_section,
            date=data["date"],
            records=data["records"],
            teacher=data["marked_by"],  
        )

        return Response(
            {
                "message": "Attendance processed",
                "created": result["created"],
                "skipped": result["skipped"],
            },
            status=status.HTTP_201_CREATED,
        )

        

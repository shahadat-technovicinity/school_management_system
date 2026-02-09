# attendance/views.py

from apps.attendance.serializers.attendance import BulkAttendanceSerializer
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import IsAuthenticated


class BulkAttendanceAPIView(CreateAPIView):
    serializer_class = BulkAttendanceSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

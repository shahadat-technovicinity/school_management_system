from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from ..models import LeaveApplication
from ..serializers.leave_serializers import LeaveApplicationSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

class LeaveApplicationViewSet(viewsets.ModelViewSet):
    queryset = LeaveApplication.objects.all()
    serializer_class = LeaveApplicationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status', 'staff', 'leave_type']

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        leave = self.get_object()
        leave.status = 'approved'
        leave.comments = request.data.get('comments', '')
        leave.save()
        return Response({'status': 'approved'})

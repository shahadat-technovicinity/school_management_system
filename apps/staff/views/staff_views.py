from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from ..models import StaffProfile, LeaveApplication, WorkAssignment, CommitteeMember, LeaveBalance
from ..serializers.staff_serializers import (
    StaffListSerializer, 
    StaffProfileDetailSerializer,
    LeaveApplicationSerializer,
    WorkAssignmentSerializer,
    CommitteeMemberSerializer,
    LeaveBalanceSerializer
)

class StaffProfileViewSet(viewsets.ModelViewSet):
    queryset = StaffProfile.objects.all().select_related('user', 'payroll').prefetch_related('leave_balances')
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'status', 'department']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name', 'phone']
    ordering_fields = ['joining_date', 'employee_id']

    def get_serializer_class(self):
        if self.action == 'list':
            return StaffListSerializer
        return StaffProfileDetailSerializer

    def perform_destroy(self, instance):
        # Cleanup user if needed, or just mark inactive
        # Here we do a hard delete as requested for CRUD fulfillment
        instance.user.delete() 
        instance.delete()

    @action(detail=False, methods=['get'])
    def teachers(self, request):
        teachers = self.queryset.filter(role='teacher')
        page = self.paginate_queryset(teachers)
        if page is not None:
            serializer = StaffListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = StaffListSerializer(teachers, many=True)
        return Response(serializer.data)

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

class WorkAssignmentViewSet(viewsets.ModelViewSet):
    queryset = WorkAssignment.objects.all()
    serializer_class = WorkAssignmentSerializer

class CommitteeViewSet(viewsets.ModelViewSet):
    queryset = CommitteeMember.objects.all()
    serializer_class = CommitteeMemberSerializer

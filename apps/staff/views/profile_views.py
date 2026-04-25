from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from ..models import StaffProfile
from ..serializers.profile_serializers import (
    StaffListSerializer, 
    StaffProfileDetailSerializer
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
        if instance.user:
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

from rest_framework import generics
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.contrib.sessions.models import Session
from django.utils import timezone
from apps.students.models import Student
from reg_mm_stock_event.models import StockInventory
from .serializers import *

User = get_user_model()


class SystemOverviewView(generics.GenericAPIView):
    serializer_class = SystemOverviewSerializer

    def get(self, request, *args, **kwargs):
        active_students = Student.objects.filter(status='active').count()

        active_staff = User.objects.filter(
            role__in=['Head Master', 'Teacher', 'Staff'], is_active=True
        ).count()

        total_assets = StockInventory.objects.count()

        active_sessions = Session.objects.filter(
            expire_date__gte=timezone.now()
        ).count()

        return Response({
            'active_students': active_students,
            'active_staff': active_staff,
            'total_assets': total_assets,
            'active_sessions': active_sessions,
        })


class SystemActivityView(generics.GenericAPIView):
    serializer_class = SystemActivitySerializer

    def get(self, request, *args, **kwargs):
        from django.contrib.auth import get_user_model
        User = get_user_model()

        # Last logged in users
        users = User.objects.filter(
            last_login__isnull=False
        ).order_by('-last_login')[:20]

        activities = []
        for user in users:
            activities.append({
                'timestamp': user.last_login,
                'user': user.name or user.username,
                'action': 'Login',
                'module': 'Authentication',
                'ip_address': '-',
                'status': 'Success',
            })

        return Response({'activities': activities})
    




class UserManagementView(generics.GenericAPIView):
    serializer_class = UserManagementSerializer

    def get(self, request, *args, **kwargs):
        users = User.objects.all().order_by('-last_login')

        total = users.count()
        active = users.filter(is_active=True).count()
        inactive = users.filter(is_active=False).count()

        data = []
        for user in users:
            data.append({
                'user_id': user.username,
                'name': user.name or user.username,
                'role': user.role,
                'last_login': user.last_login,
                'account_status': 'Active' if user.is_active else 'Inactive',
            })

        return Response({
            'stats': {
                'total_users': total,
                'active_users': active,
                'inactive_users': inactive,
            },
            'users': data,
        })


class InventoryManagementView(generics.GenericAPIView):
    serializer_class = InventoryManagementSerializer

    def get(self, request, *args, **kwargs):
        inventories = StockInventory.objects.all()

        total = inventories.count()
        in_stock = sum(1 for i in inventories if i.status == 'In Stock')
        low_stock = sum(1 for i in inventories if i.status == 'Low Stock')
        out_of_stock = sum(1 for i in inventories if i.status == 'Out of Stock')

        data = []
        for item in inventories:
            data.append({
                'id': item.id,
                'category': item.display_category,
                'item_name': item.item_name,
                'quantity': item.quantity,
                'total_capacity': item.total_capacity,
                'status': item.status,
                'notes': item.notes,
            })

        return Response({
            'stats': {
                'total_assets': total,
                'in_stock': in_stock,
                'low_stock': low_stock,
                'out_of_stock': out_of_stock,
            },
            'inventory': data,
        })
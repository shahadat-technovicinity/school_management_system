from rest_framework import serializers
from django.contrib.auth import get_user_model
from ..models import StaffProfile, StaffPayroll, LeaveApplication, WorkAssignment, CommitteeMember

User = get_user_model()

class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']

class StaffPayrollSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffPayroll
        fields = '__all__'

class StaffListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.get_full_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = StaffProfile
        fields = [
            'id', 'employee_id', 'name', 'email', 'role', 
            'designation', 'phone', 'joining_date', 'status'
        ]

class StaffProfileDetailSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    payroll = StaffPayrollSerializer(read_only=True)
    
    class Meta:
        model = StaffProfile
        fields = '__all__'

class LeaveApplicationSerializer(serializers.ModelSerializer):
    staff_name = serializers.CharField(source='staff.user.get_full_name', read_only=True)
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)

    class Meta:
        model = LeaveApplication
        fields = '__all__'

class WorkAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkAssignment
        fields = '__all__'

class CommitteeMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommitteeMember
        fields = '__all__'

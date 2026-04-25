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

class LeaveBalanceSerializer(serializers.ModelSerializer):
    leave_type_name = serializers.CharField(source='leave_type.name', read_only=True)
    class Meta:
        model = LeaveBalance
        fields = ['id', 'leave_type_name', 'total_allocated', 'used', 'remaining', 'academic_year']

class StaffProfileDetailSerializer(serializers.ModelSerializer):
    user = UserShortSerializer(read_only=True)
    payroll = StaffPayrollSerializer(required=False)
    leave_balances = LeaveBalanceSerializer(many=True, read_only=True)
    
    class Meta:
        model = StaffProfile
        fields = '__all__'

    def create(self, validated_data):
        payroll_data = validated_data.pop('payroll', None)
        profile = StaffProfile.objects.create(**validated_data)
        if payroll_data:
            StaffPayroll.objects.create(staff=profile, **payroll_data)
        return profile

    def update(self, instance, validated_data):
        payroll_data = validated_data.pop('payroll', None)
        
        # Update Profile fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Update or Create Payroll
        if payroll_data:
            payroll_instance, created = StaffPayroll.objects.get_or_create(staff=instance)
            for attr, value in payroll_data.items():
                setattr(payroll_instance, attr, value)
            payroll_instance.save()
            
        return instance

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

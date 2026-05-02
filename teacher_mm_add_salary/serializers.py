from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import SalaryRecord, Allowance, Deduction, ExtraWork, PaymentHistory

User = get_user_model()


class EmployeeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'role']


class AllowanceSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)

    class Meta:
        model = Allowance
        fields = ['id', 'name', 'amount']


class DeductionSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    amount = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)

    class Meta:
        model = Deduction
        fields = ['id', 'name', 'amount']


class ExtraWorkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtraWork
        fields = ['id', 'work_type', 'hours', 'rate_per_hour']


class PaymentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentHistory
        fields = ['id', 'month', 'year', 'net_salary', 'status', 'payment_date']


class SalaryRecordSerializer(serializers.ModelSerializer):
    allowances = AllowanceSerializer(many=True, required=False)
    deductions = DeductionSerializer(many=True, required=False)
    extra_works = ExtraWorkSerializer(many=True, required=False)
    payment_history = PaymentHistorySerializer(many=True, read_only=True)
    employee_name = serializers.SerializerMethodField(read_only=True)
    total_allowances = serializers.SerializerMethodField(read_only=True)
    total_deductions = serializers.SerializerMethodField(read_only=True)
    net_salary = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = SalaryRecord
        fields = [
            'id', 'employee', 'employee_name', 'department', 'position',
            'basic_salary', 'payment_frequency', 'payment_method', 'status',
            'comments', 'allowances', 'deductions', 'extra_works',
            'total_allowances', 'total_deductions', 'net_salary',
            'payment_history', 'created_at'
        ]
        read_only_fields = ['created_at', 'status']

    def get_employee_name(self, obj):
        return obj.employee.name

    def get_total_allowances(self, obj):
        allowances = sum(a.amount for a in obj.allowances.all() if a.amount)
        extra = sum(e.hours * e.rate_per_hour for e in obj.extra_works.all())
        return allowances + extra

    def get_total_deductions(self, obj):
        return sum(d.amount for d in obj.deductions.all() if d.amount)

    def get_net_salary(self, obj):
        total_allowances = sum(a.amount for a in obj.allowances.all() if a.amount)
        extra = sum(e.hours * e.rate_per_hour for e in obj.extra_works.all())
        total_deductions = sum(d.amount for d in obj.deductions.all() if d.amount)
        return obj.basic_salary + total_allowances + extra - total_deductions

    def create(self, validated_data):
        allowances_data = validated_data.pop('allowances', [])
        deductions_data = validated_data.pop('deductions', [])
        extra_works_data = validated_data.pop('extra_works', [])

        salary_record = SalaryRecord.objects.create(**validated_data)

        for allowance in allowances_data:
            Allowance.objects.create(salary_record=salary_record, **allowance)
        for deduction in deductions_data:
            Deduction.objects.create(salary_record=salary_record, **deduction)
        for extra in extra_works_data:
            ExtraWork.objects.create(salary_record=salary_record, **extra)

        return salary_record

    def update(self, instance, validated_data):
        allowances_data = validated_data.pop('allowances', [])
        deductions_data = validated_data.pop('deductions', [])
        extra_works_data = validated_data.pop('extra_works', [])

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        instance.allowances.all().delete()
        for allowance in allowances_data:
            Allowance.objects.create(salary_record=instance, **allowance)

        instance.deductions.all().delete()
        for deduction in deductions_data:
            Deduction.objects.create(salary_record=instance, **deduction)

        instance.extra_works.all().delete()
        for extra in extra_works_data:
            ExtraWork.objects.create(salary_record=instance, **extra)

        return instance
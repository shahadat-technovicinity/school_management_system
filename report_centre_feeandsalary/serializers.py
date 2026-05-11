from rest_framework import serializers


class FeeCollectionReportSerializer(serializers.Serializer):
    total_collected = serializers.DecimalField(max_digits=12, decimal_places=2)
    pending = serializers.DecimalField(max_digits=12, decimal_places=2)
    overdue = serializers.DecimalField(max_digits=12, decimal_places=2)
    collection_rate = serializers.FloatField()


class SalaryDisbursementReportSerializer(serializers.Serializer):
    total_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_staff = serializers.IntegerField()
    average_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    disbursement_rate = serializers.FloatField()


class FinancialSummarySerializer(serializers.Serializer):
    month = serializers.CharField()
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    fee_collection = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expense = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
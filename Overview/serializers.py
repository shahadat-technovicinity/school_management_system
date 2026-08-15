from rest_framework import serializers

class AccountStatsSerializer(serializers.Serializer):
    todays_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    todays_expense = serializers.DecimalField(max_digits=12, decimal_places=2)
    todays_pending = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_balance = serializers.DecimalField(max_digits=12, decimal_places=2)
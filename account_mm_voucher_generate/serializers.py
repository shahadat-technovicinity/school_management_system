from rest_framework import serializers
from .models import ExpenseVoucher

class ExpenseVoucherSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseVoucher
        fields = ['date', 'deposit_category', 'amount', 'description']
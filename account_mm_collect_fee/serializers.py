from rest_framework import serializers
from .models import FeeCollection, FeeCollectionItem


class FeeCollectionItemSerializer(serializers.ModelSerializer):
    fee_type = serializers.CharField(source='fee.fee_type', read_only=True)

    class Meta:
        model = FeeCollectionItem
        fields = ['id', 'fee', 'fee_type', 'amount']


class FeeCollectionSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField(read_only=True)
    items = FeeCollectionItemSerializer(many=True, read_only=True)

    class Meta:
        model = FeeCollection
        fields = '__all__'
        ref_name = 'FeeCollectionMain'
        extra_kwargs = {
            'total_amount': {'required': False},
            'discount_amount': {'required': False},
            'final_amount': {'required': False},
            'payment_method': {'required': False},
            'transaction_id': {'required': False},
            'payment_date': {'required': False},
            'notes': {'required': False},
            'status': {'required': False},
        }

    def get_student_name(self, obj):
        return obj.student.full_name


class OutstandingFeeSerializer(serializers.Serializer):
    fee_id = serializers.IntegerField()
    fee_type = serializers.CharField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    due_date = serializers.DateField()
    status = serializers.CharField()
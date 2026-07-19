from rest_framework import serializers
from apps.admissions.models import LotterySession


class LotterySessionSerializer(serializers.ModelSerializer):
    """Full serializer for LotterySession CRUD."""

    class Meta:
        model = LotterySession
        fields = [
            'id',
            'academic_year',
            'target_class',
            'total_seats',
            'lottery_date',
            'is_completed',
            'created_at',
        ]
        read_only_fields = ['id', 'is_completed', 'created_at']


class LotteryStatsSerializer(serializers.Serializer):
    """Validates the `?class=` query param for the stats endpoint."""
    class_name = serializers.CharField(required=False, default='class 6')

    def to_internal_value(self, data):
        # Accept `class` from query params and map it to class_name
        mutable = {'class_name': data.get('class', 'class 6')}
        return super().to_internal_value(mutable)


class AssignNumbersSerializer(serializers.Serializer):
    """Validates payload for assigning sequential admin form numbers."""
    class_name = serializers.CharField(required=True)

    def to_internal_value(self, data):
        mutable = {'class_name': data.get('class', data.get('class_name'))}
        return super().to_internal_value(mutable)


class ExecuteLotterySerializer(serializers.Serializer):
    """Validates payload for executing the lottery draw."""
    class_name = serializers.CharField(required=True)
    seats = serializers.IntegerField(required=False, min_value=1)

    def to_internal_value(self, data):
        mutable = {
            'class_name': data.get('class', data.get('class_name')),
            'seats': data.get('seats'),
        }
        # Drop seats if not provided so it can be resolved dynamically
        if mutable['seats'] in (None, ''):
            mutable.pop('seats')
        return super().to_internal_value(mutable)
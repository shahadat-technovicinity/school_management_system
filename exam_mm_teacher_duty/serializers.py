from rest_framework import serializers
from .models import ExamDuty


class ExamDutySerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.get_full_name', read_only=True)
    teacher_email = serializers.CharField(source='teacher.email', read_only=True)

    class Meta:
        model = ExamDuty
        fields = [
            'id',
            'teacher',
            'teacher_name',
            'teacher_email',
            'exam_date',
            'start_time',
            'end_time',
            'room_number',
            'status',
            'send_notification',
            'created_at'
        ]
        read_only_fields = ['status', 'created_at']

    def validate(self, attrs):
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')

        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError({"end_time": "End time must be after start time."})

        return attrs


class ExamDutyStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamDuty
        fields = ['status']

    def validate_status(self, value):
        allowed_statuses = ['Pending', 'Confirmed', 'Conflict']
        if value not in allowed_statuses:
            raise serializers.ValidationError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return value
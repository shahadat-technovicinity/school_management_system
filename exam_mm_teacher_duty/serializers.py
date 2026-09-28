from rest_framework import serializers
from .models import ExamDuty


class ExamDutySerializer(serializers.ModelSerializer):
    teacher_name = serializers.SerializerMethodField()
    teacher_designation = serializers.ReadOnlyField(source='teacher.designation', default="")
    teacher_phone = serializers.ReadOnlyField(source='teacher.primary_contact_number', default="")

    class Meta:
        model = ExamDuty
        fields = [
            'id',
            'teacher',
            'teacher_name',
            'teacher_designation',
            'teacher_phone',
            'exam_date',
            'start_time',
            'end_time',
            'room_number',
            'status',
            'send_notification',
            'created_at'
        ]
        read_only_fields = ['status', 'created_at']

    def get_teacher_name(self, obj):
        if not obj.teacher:
            return ""
        
        # 1. First check user account full name
        if obj.teacher.user:
            if hasattr(obj.teacher.user, 'get_full_name') and callable(obj.teacher.user.get_full_name):
                full_name = obj.teacher.user.get_full_name()
                if full_name:
                    return full_name
            if getattr(obj.teacher.user, 'first_name', None):
                return f"{obj.teacher.user.first_name} {getattr(obj.teacher.user, 'last_name', '')}".strip()
            if getattr(obj.teacher.user, 'username', None):
                return obj.teacher.user.username

        # 2. Fallback to Bangla name
        if obj.teacher.name_bn:
            return obj.teacher.name_bn

        return f"Teacher ID: {obj.teacher.id}"

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
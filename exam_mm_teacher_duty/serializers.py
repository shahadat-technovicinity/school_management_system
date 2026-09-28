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

        # ১. প্রফাইলে বাংলা নাম থাকলে আগে সেটা নিবে
        if getattr(obj.teacher, 'name_bn', None):
            return obj.teacher.name_bn

        # ২. ইউজার অ্যাকাউন্টের Full Name / First & Last Name চেক করবে
        if obj.teacher.user:
            if hasattr(obj.teacher.user, 'get_full_name') and callable(obj.teacher.user.get_full_name):
                full_name = obj.teacher.user.get_full_name()
                if full_name:
                    return full_name

            first_name = getattr(obj.teacher.user, 'first_name', '')
            last_name = getattr(obj.teacher.user, 'last_name', '')
            if first_name or last_name:
                return f"{first_name} {last_name}".strip()

            if getattr(obj.teacher.user, 'username', None):
                return obj.teacher.user.username

        return f"Teacher #{obj.teacher.id}"

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
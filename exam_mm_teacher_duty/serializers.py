from rest_framework import serializers
from .models import ExamDuty


class ExamDutySerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(source='teacher.name', read_only=True)
    subject_name = serializers.CharField(source='subject.name', read_only=True)

    class Meta:
        model = ExamDuty
        fields = [
            'id', 'teacher', 'teacher_name', 'subject', 'subject_name',
            'exam_date', 'time_slot', 'room_number', 'status',
            'send_notification', 'created_at'
        ]
        read_only_fields = ['status']


class ExamDutyStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExamDuty
        fields = ['status']
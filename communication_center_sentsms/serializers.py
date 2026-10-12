from rest_framework import serializers
from .models import SMSHistory


class SMSHistorySerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)
    template_title = serializers.CharField(source='template.title', read_only=True)

    class Meta:
        model = SMSHistory
        fields = '__all__'
        ref_name = 'NotificationsSMSHistorySerializer'
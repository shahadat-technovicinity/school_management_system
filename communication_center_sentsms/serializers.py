from rest_framework import serializers
from .models import SMSTemplate, SMSHistory


class SMSTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSTemplate
        fields = '__all__'
        ref_name = 'NotificationsSMSTemplateSerializer'


class SMSHistorySerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source='student.full_name', read_only=True)

    class Meta:
        model = SMSHistory
        fields = '__all__'
        ref_name = 'NotificationsSMSHistorySerializer'
from rest_framework import serializers
from .models import *

class SMSSentHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSSentHistory
        fields = '__all__'


class SendSMSSerializer(serializers.Serializer):
    GROUP_CHOICES = [
        ('all_teachers', 'All Teachers'),
        ('all_staff', 'All Staff'),
        ('all_students', 'All Students'),
        ('all_parents', 'All Parents'),
        ('class_6', 'Class 6'),
        ('class_7', 'Class 7'),
        ('class_8', 'Class 8'),
        ('class_9', 'Class 9'),
        ('class_10', 'Class 10'),
    ]

    template_id = serializers.IntegerField(required=False, allow_null=True)
    message = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    group = serializers.ChoiceField(choices=GROUP_CHOICES)
    schedule = serializers.DateTimeField(required=False, allow_null=True)

    def validate(self, data):
        if not data.get('template_id') and not data.get('message'):
            raise serializers.ValidationError('Either template_id or message is required.')
        return data


class SMSStatsSerializer(serializers.Serializer):
    total_sent = serializers.IntegerField()
    sent_this_month = serializers.IntegerField()
    success = serializers.IntegerField()
    failed = serializers.IntegerField()
    pending = serializers.IntegerField()
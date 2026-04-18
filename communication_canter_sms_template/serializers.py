from rest_framework import serializers
from .models import SMSTemplate

class SMSTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SMSTemplate
        fields = '__all__'
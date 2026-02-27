from rest_framework import serializers
from .models import *

class NoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = communication_center_notice
        fields = '__all__'

    def validate_publish_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("Publish date cannot be in the past.")
        return value
    

class LetterIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = LetterIssue
        fields = '__all__'

    def validate_issue_date(self, value):
        if value < timezone.now().date():
            raise serializers.ValidationError("Issue date cannot be in the past.")
        return value
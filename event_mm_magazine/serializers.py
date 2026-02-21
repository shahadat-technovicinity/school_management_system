from rest_framework import serializers
from .models import *

class MagazineIssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = MagazineIssue
        fields = '__all__'


##### New Serializer for Scheduled Publication
class ScheduledPublicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScheduledPublication
        fields = '__all__'



### New Serializer for Content Submission
class ContentSubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentSubmission
        fields = '__all__'
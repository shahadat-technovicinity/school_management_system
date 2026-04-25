from rest_framework import serializers
from ..models import CommitteeMember, CommitteeNotice, CommitteeCommunication

class CommitteeMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommitteeMember
        fields = '__all__'

class CommitteeNoticeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommitteeNotice
        fields = '__all__'

class CommitteeCommunicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommitteeCommunication
        fields = '__all__'

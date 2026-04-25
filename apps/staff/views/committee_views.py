from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from ..models import CommitteeMember, CommitteeNotice, CommitteeCommunication
from ..serializers.committee_serializers import (
    CommitteeMemberSerializer, 
    CommitteeNoticeSerializer, 
    CommitteeCommunicationSerializer
)

class CommitteeViewSet(viewsets.ModelViewSet):
    queryset = CommitteeMember.objects.all()
    serializer_class = CommitteeMemberSerializer

class CommitteeNoticeViewSet(viewsets.ModelViewSet):
    queryset = CommitteeNotice.objects.all().order_by('-created_at')
    serializer_class = CommitteeNoticeSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['committee_type', 'status']

class CommitteeCommunicationViewSet(viewsets.ModelViewSet):
    queryset = CommitteeCommunication.objects.all().order_by('-sent_at')
    serializer_class = CommitteeCommunicationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['committee_type', 'message_type']

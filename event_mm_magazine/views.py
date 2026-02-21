from rest_framework import generics
from .models import *
from .serializers import *
from rest_framework.parsers import MultiPartParser, FormParser


class MagazineIssueCreateView(generics.CreateAPIView):
    queryset = MagazineIssue.objects.all()
    serializer_class = MagazineIssueSerializer
    parser_classes = (MultiPartParser, FormParser)


class MagazineUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MagazineIssue.objects.all()
    serializer_class = MagazineIssueSerializer
    lookup_field = 'pk'
    parser_classes = (MultiPartParser, FormParser)



### New View for Scheduled Publication Creation
class SchedulePublicationCreateView(generics.CreateAPIView):
    queryset = ScheduledPublication.objects.all()
    serializer_class = ScheduledPublicationSerializer
    parser_classes = (MultiPartParser, FormParser)


class SchedulePublicationUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ScheduledPublication.objects.all()
    serializer_class = ScheduledPublicationSerializer
    lookup_field = 'pk'
    parser_classes = (MultiPartParser, FormParser)




#### New View for Content Submission Creation
class ContentSubmissionCreateView(generics.CreateAPIView):
    queryset = ContentSubmission.objects.all()
    serializer_class = ContentSubmissionSerializer
    parser_classes = (MultiPartParser, FormParser)


class ContentSubmissionUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ContentSubmission.objects.all()
    serializer_class = ContentSubmissionSerializer
    lookup_field = 'pk'
    parser_classes = (MultiPartParser, FormParser)

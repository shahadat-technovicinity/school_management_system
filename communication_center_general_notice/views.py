from rest_framework import generics, parsers
from .models import *
from .serializers import *
from rest_framework.views import APIView
from rest_framework.response import Response




class NoticeListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = NoticeSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    
    
    def get_queryset(self):
        return communication_center_notice.objects.all().order_by('-created_at')
    
    def get_queryset(self):
        today = timezone.now().date()
        is_archive_request = self.request.query_params.get('tab') == 'archive'
        
        if is_archive_request:
            return communication_center_notice.objects.filter(publish_date__lt=today).order_by('-publish_date')
        else:
            return communication_center_notice.objects.filter(publish_date__gte=today).order_by('-publish_date')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        general_notices = queryset.filter(notice_type='general')
        co_education_notices = queryset.filter(notice_type='co_education')

        general_serializer = self.get_serializer(general_notices, many=True)
        co_education_serializer = self.get_serializer(co_education_notices, many=True)

        return Response({
            "general_notices": general_serializer.data,
            "co_education_notices": co_education_serializer.data
        })

class NoticeDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = communication_center_notice.objects.all()
    serializer_class = NoticeSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]




### Letter Issue Views for Communication Center
class LetterIssueListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = LetterIssueSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]
    
    def get_queryset(self):
        # All letters ordered by creation date (newest first)
        return LetterIssue.objects.all().order_by('-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        all_letters_data = self.get_serializer(queryset, many=True).data

        # status filtering
        pending_letters = queryset.filter(status='pending')
        approved_letters = queryset.filter(status='approved')

        # response format
        return Response({
            "all_letters": all_letters_data,
            "pending_letters": self.get_serializer(pending_letters, many=True).data,
            "approved_letters": self.get_serializer(approved_letters, many=True).data
        })


class LetterIssueDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LetterIssue.objects.all()
    serializer_class = LetterIssueSerializer
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

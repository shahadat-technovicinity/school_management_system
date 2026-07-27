from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated

from .models import Mail, Attachment
from .serializers import MailListSerializer, MailDetailSerializer, MailCreateSerializer
from .smtp_service import send_via_smtp


class MailListView(generics.ListAPIView):
    """ শুধু sender নিজে যা পাঠিয়েছে সেটার লিস্ট (sent/draft/trash) """
    permission_classes = [IsAuthenticated]
    serializer_class = MailListSerializer

    def get_queryset(self):
        user = self.request.user
        folder = self.request.query_params.get('folder', 'sent')
        return Mail.objects.filter(sender=user, folder=folder).prefetch_related('attachments')


class MailCreateView(generics.CreateAPIView):
    """ একক বা bulk মেইল পাঠানো (to_emails এ কমা দিয়ে একাধিক email দিন) """
    permission_classes = [IsAuthenticated]
    serializer_class = MailCreateSerializer
    parser_classes = [MultiPartParser, FormParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mail = serializer.save()

        for f in request.FILES.getlist('attachments'):
            if f.size <= 10 * 1024 * 1024:  # ম্যাক্স ১০ এমবি প্রতি ফাইল
                Attachment.objects.create(mail=mail, file=f, filename=f.name, file_size=f.size)

        smtp_ok = send_via_smtp(mail)
        recipient_count = len([e for e in mail.to_emails.split(',') if e.strip()])

        return Response({
            'mail': MailDetailSerializer(mail, context={'request': request}).data,
            'smtp_sent': smtp_ok,
            'recipient_count': recipient_count,
            'message': f'{recipient_count} জনকে মেইল পাঠানো হয়েছে ✅' if smtp_ok else 'মেইল সেভ হয়েছে কিন্তু SMTP পাঠাতে ব্যর্থ হয়েছে।'
        }, status=status.HTTP_201_CREATED if smtp_ok else status.HTTP_502_BAD_GATEWAY)


class MailDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MailDetailSerializer

    def get_queryset(self):
        return Mail.objects.filter(sender=self.request.user)
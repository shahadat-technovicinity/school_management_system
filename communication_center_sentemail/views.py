from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from .models import Mail, Attachment
from .serializers import (
    UserSerializer,
    MailListSerializer,
    MailDetailSerializer,
    MailCreateSerializer,
    MoveFolderSerializer,
)
from .smtp_service import send_via_smtp

class UserListView(generics.ListAPIView):
    """ মেইল টাইপ করার সময় টু-ফিল্ডে (Recipient picker) সাজেস্ট করার জন্য ইউজার লিস্ট """
    permission_classes = [IsAuthenticated]
    serializer_class   = UserSerializer

    def get_queryset(self):
        q = self.request.query_params.get('search', '').strip()
        qs = User.objects.exclude(id=self.request.user.id)
        if q:
            qs = qs.filter(
                Q(username__icontains=q) | Q(email__icontains=q) |
                Q(first_name__icontains=q) | Q(last_name__icontains=q)
            )
        return qs


class MailListView(generics.ListAPIView):
    """ ফিগমার বাম পাশের মেনু ফিল্টারিং (Inbox, Sent, Draft, Trash, Parents, Teachers) """
    permission_classes = [IsAuthenticated]
    serializer_class   = MailListSerializer

    def get_queryset(self):
        user = self.request.user
        folder = self.request.query_params.get('folder', 'inbox')

        if folder == 'inbox':
            # ইনবক্স = অন্য কেউ আপনাকে পাঠিয়েছে এবং মেইলটি ট্র্যাশে যায়নি
            return Mail.objects.filter(to_emails__icontains=user.email, folder='sent').prefetch_related('attachments')
        elif folder in ['parents', 'teachers']:
            # কাস্টম ক্যাটাগরি ফোল্ডার ফিল্টার লজিক
            return Mail.objects.filter(sender=user, folder=folder).prefetch_related('attachments')
        else:
            # sent, draft, trash এর জন্য ইউজার নিজেই ওনার
            return Mail.objects.filter(sender=user, folder=folder).prefetch_related('attachments')


class MailCreateView(generics.CreateAPIView):
    """ নতুন মেইল কম্পোজ করা এবং জিমেইল এসটিটিপি দিয়ে রিয়েল টাইমে পাঠানো """
    # permission_classes = [IsAuthenticated]
    serializer_class   = MailCreateSerializer
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mail = serializer.save()

        # ফাইল অ্যাটাচমেন্ট সেভ করা (সর্বোচ্চ ১০ এমবি)
        for f in request.FILES.getlist('attachments'):
            if f.size <= 10 * 1024 * 1024:
                Attachment.objects.create(mail=mail, file=f, filename=f.name, file_size=f.size)

        smtp_ok = False
        if mail.folder == 'sent':
            smtp_ok = send_via_smtp(mail)

        return Response({
            'mail': MailDetailSerializer(mail, context={'request': request}).data,
            'smtp_sent': smtp_ok,
            'message': 'মেইল সফলভাবে পাঠানো হয়েছে ✅' if smtp_ok else 'মেইলটি ড্রাফট হিসেবে সেভ হয়েছে।'
        }, status=status.HTTP_201_CREATED)


class MailDetailView(generics.RetrieveAPIView):
    """ যেকোনো একটি নির্দিষ্ট মেইল ওপেন করে দেখা (ইনবক্স বা সেন্ট দুটোই কাজ করবে) """
    permission_classes = [IsAuthenticated]
    serializer_class   = MailDetailSerializer

    def get_queryset(self):
        user = self.request.user
        return Mail.objects.filter(Q(sender=user) | Q(to_emails__icontains=user.email))

    def retrieve(self, request, *args, **kwargs):
        mail = self.get_object()
        # রিড করা না হয়ে থাকলে অটোমেটিক রিড মার্ক হবে
        if not mail.is_read and request.user.email in mail.to_emails:
            mail.is_read = True
            mail.save(update_fields=['is_read'])
        
        serializer = self.get_serializer(mail)
        return Response(serializer.data)


class MailDeleteView(generics.DestroyAPIView):
    """ প্রথম ক্লিকে Trash এ যাবে, Trash এ থাকা অবস্থায় ক্লিকে পার্মানেন্ট ডিলিট হবে """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Mail.objects.filter(Q(sender=user) | Q(to_emails__icontains=user.email))

    def destroy(self, request, *args, **kwargs):
        mail = self.get_object()
        if mail.folder == 'trash':
            mail.delete()
            return Response({'message': 'মেইলটি চিরতরে ডিলিট করা হয়েছে।'}, status=status.HTTP_204_NO_CONTENT)
        
        mail.folder = 'trash'
        mail.save(update_fields=['folder'])
        return Response({'message': 'মেইলটি ট্র্যাশে সরানো হয়েছে।'})


class MailStarToggleView(APIView):
    """ ফিগমার মেইল লিস্টের স্টারে ক্লিক করলে অন/অফ হবে """
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        user = request.user
        mail = get_object_or_404(Mail, Q(sender=user) | Q(to_emails__icontains=user.email), pk=pk)
        mail.is_starred = not mail.is_starred
        mail.save(update_fields=['is_starred'])
        return Response({'is_starred': mail.is_starred})


class MailMoveFolderView(generics.UpdateAPIView):
    """ মেইল ড্রপডাউন থেকে Parents বা Teachers ফোল্ডারে মুভ করার জন্য """
    permission_classes = [IsAuthenticated]
    serializer_class   = MoveFolderSerializer
    http_method_names  = ['patch']

    def get_queryset(self):
        return Mail.objects.filter(sender=self.request.user)


class MailReplyView(generics.CreateAPIView):
    """ ফিগমার ৫ নম্বর ফ্রেমের 'Reply' পপআপের ব্যাকএন্ড এপিআই """
    permission_classes = [IsAuthenticated]
    serializer_class   = MailCreateSerializer
    parser_classes     = [MultiPartParser, FormParser, JSONParser]

    def create(self, request, *args, **kwargs):
        original = get_object_or_404(Mail, pk=self.kwargs['pk'])
        
        data = {
            'to_emails' : original.sender.email,
            'subject'   : f"Re: {original.subject}" if not original.subject.startswith("Re:") else original.subject,
            'body'      : request.data.get('body', ''),
            'reply_to'  : original.pk,
            'action'    : request.data.get('action', 'send'),
        }
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        mail = serializer.save()

        for f in request.FILES.getlist('attachments'):
            if f.size <= 10 * 1024 * 1024:
                Attachment.objects.create(mail=mail, file=f, filename=f.name, file_size=f.size)

        smtp_ok = send_via_smtp(mail) if mail.folder == 'sent' else False
        return Response({
            'mail': MailDetailSerializer(mail, context={'request': request}).data,
            'smtp_sent': smtp_ok,
            'message': 'রিপ্লাই সফলভাবে পাঠানো হয়েছে ✅' if smtp_ok else 'ড্রাফট সেভ হয়েছে।'
        }, status=status.HTTP_201_CREATED)


class UnreadCountView(APIView):
    """ সাইডবারের ইনবক্স ব্যাজে (Badge) কাউন্ট দেখানোর জন্য """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Mail.objects.filter(to_emails__icontains=request.user.email, folder='sent', is_read=False).count()
        return Response({'unread_count': count})
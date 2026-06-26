from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Mail, Attachment

class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model  = User
        fields = ['id', 'username', 'email', 'full_name']

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username


class AttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model  = Attachment
        fields = ['id', 'filename', 'file_size', 'file_url', 'uploaded_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class MailListSerializer(serializers.ModelSerializer):
    sender_name     = serializers.SerializerMethodField()
    sender_email    = serializers.SerializerMethodField()
    has_attachments = serializers.SerializerMethodField()

    class Meta:
        model  = Mail
        fields = [
            'id', 'sender_name', 'sender_email',
            'to_emails', 'subject', 'folder',
            'is_read', 'is_starred',
            'has_attachments', 'created_at',
        ]

    def get_sender_name(self, obj):
        return obj.sender.get_full_name() or obj.sender.username

    def get_sender_email(self, obj):
        return obj.sender.email

    def get_has_attachments(self, obj):
        return obj.attachments.exists()


class MailDetailSerializer(serializers.ModelSerializer):
    sender           = UserSerializer(read_only=True)
    attachments      = AttachmentSerializer(many=True, read_only=True)
    reply_to_subject = serializers.SerializerMethodField()

    class Meta:
        model  = Mail
        fields = [
            'id', 'sender', 'to_emails',
            'subject', 'body', 'folder',
            'is_read', 'is_starred',
            'smtp_sent', 'smtp_error',
            'reply_to', 'reply_to_subject',
            'attachments', 'created_at', 'updated_at',
        ]

    def get_reply_to_subject(self, obj):
        return obj.reply_to.subject if obj.reply_to else None


class MailCreateSerializer(serializers.ModelSerializer):
    action = serializers.ChoiceField(choices=['send', 'draft'], default='send', write_only=True)

    class Meta:
        model  = Mail
        fields = ['to_emails', 'subject', 'body', 'reply_to', 'action']

    def validate_to_emails(self, value):
        emails = [e.strip() for e in value.split(',') if e.strip()]
        if not emails:
            raise serializers.ValidationError("অন্তত একটি বৈধ ইমেইল অ্যাড্রেস দিন।")
        return ', '.join(emails)

    def create(self, validated_data):
        action = validated_data.pop('action', 'send')
        validated_data['sender'] = self.context['request'].user
        # ইউজার যদি সেন্ড করে তবে 'sent' ফোল্ডার, অন্যথায় 'draft'
        validated_data['folder'] = 'sent' if action == 'send' else 'draft'
        return super().create(validated_data)


class MoveFolderSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Mail
        fields = ['folder']

    def validate_folder(self, value):
        valid = ['inbox', 'sent', 'draft', 'trash', 'parents', 'teachers']
        if value not in valid:
            raise serializers.ValidationError(f"বৈধ ফোল্ডারগুলো হলো: {valid}")
        return value
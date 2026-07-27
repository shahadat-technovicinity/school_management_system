from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Mail, Attachment

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'name', 'phone_number']


class AttachmentSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Attachment
        fields = ['id', 'filename', 'file_size', 'file_url', 'uploaded_at']

    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None


class MailListSerializer(serializers.ModelSerializer):
    sender_name = serializers.CharField(source='sender.name', read_only=True)
    has_attachments = serializers.SerializerMethodField()

    class Meta:
        model = Mail
        fields = [
            'id', 'sender_name', 'to_emails', 'subject',
            'folder', 'is_read', 'is_starred',
            'smtp_sent', 'smtp_error', 'has_attachments', 'created_at',
        ]

    def get_has_attachments(self, obj):
        return obj.attachments.exists()


class MailDetailSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)

    class Meta:
        model = Mail
        fields = [
            'id', 'sender', 'to_emails', 'subject', 'body', 'folder',
            'is_read', 'is_starred', 'smtp_sent', 'smtp_error',
            'reply_to', 'attachments', 'created_at', 'updated_at',
        ]


from communication_canter_sms_template.models import SMSTemplate

class MailCreateSerializer(serializers.ModelSerializer):
    template = serializers.PrimaryKeyRelatedField(
        queryset=SMSTemplate.objects.all(),
        required=False,
        write_only=True,
    )
    subject = serializers.CharField(required=False, allow_blank=True)
    body = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Mail
        fields = ['to_emails', 'subject', 'body', 'reply_to', 'template']

    def validate(self, attrs):
        template = attrs.pop('template', None)
        if template:
            attrs['subject'] = attrs.get('subject') or template.template_name
            attrs['body'] = attrs.get('body') or template.template_content
        if not attrs.get('subject'):
            raise serializers.ValidationError({"subject": "subject অথবা template — যেকোনো একটি দিতে হবে।"})
        if not attrs.get('body'):
            raise serializers.ValidationError({"body": "body অথবা template — যেকোনো একটি দিতে হবে।"})
        return attrs

    def validate_to_emails(self, value):
        emails = [e.strip() for e in value.split(',') if e.strip()]
        if not emails:
            raise serializers.ValidationError("অন্তত একটি বৈধ ইমেইল অ্যাড্রেস দিন।")
        return ', '.join(emails)

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        validated_data['folder'] = 'sent'
        return super().create(validated_data)





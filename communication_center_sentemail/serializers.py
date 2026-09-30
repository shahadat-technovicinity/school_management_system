from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Mail, Attachment
from communication_canter_sms_template.models import SMSTemplate
from apps.students.models import Student

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


class MailCreateSerializer(serializers.ModelSerializer):
    template = serializers.PrimaryKeyRelatedField(
        queryset=SMSTemplate.objects.all(),
        required=False,
        write_only=True,
    )
    to_emails = serializers.CharField(required=False, allow_blank=True)
    class_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    section_id = serializers.IntegerField(required=False, allow_null=True, write_only=True)
    subject = serializers.CharField(required=False, allow_blank=True)
    body = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Mail
        fields = ['to_emails', 'class_id', 'section_id', 'subject', 'body', 'reply_to', 'template']

    def validate(self, attrs):
        template = attrs.pop('template', None)
        class_id = attrs.pop('class_id', None)
        section_id = attrs.pop('section_id', None)
        to_emails = attrs.get('to_emails', '').strip()

        # --- ১. ইমেইল প্রাপক প্রস্তুতকরণের লজিক ---
        final_emails = []

        if to_emails:
            # ম্যানুয়ালি দেওয়া ইমেইলগুলো প্রসেস করবে
            final_emails = [e.strip() for e in to_emails.split(',') if e.strip()]
            
        elif class_id and section_id:
            # Class এবং Section অনুযায়ী স্টুডেন্ট অভিভাবকের ইমেইল ফিল্টার
            students = Student.objects.filter(
                class_name_static_id=class_id,
                section_static_id=section_id,
                status="active"
            ).select_related('guardian_info')

            collected_emails = []
            for st in students:
                if hasattr(st, 'guardian_info'):
                    # guardian_email না পাওয়া গেলে বাবা বা মায়ের ইমেইল চেক করবে
                    email = (
                        st.guardian_info.guardian_email 
                        or st.guardian_info.father_email 
                        or st.guardian_info.mother_email
                    )
                    if email and email.strip():
                        collected_emails.append(email.strip())

            # ডুপ্লিকেট ইমেইল বাদ দেওয়ার জন্য set ব্যবহার
            final_emails = list(set(collected_emails))

        if not final_emails:
            raise serializers.ValidationError({
                "to_emails": "হয় 'to_emails' ফিল্ডে ইমেইল দিন, অথবা 'class_id' ও 'section_id' নির্বাচন করুন যেখানে অভিভাবকদের ইমেইল যুক্ত আছে।"
            })

        attrs['to_emails'] = ', '.join(final_emails)

        # --- ২. ডাইনামিক টেমপ্লেট লজিক ---
        if template:
            attrs['subject'] = attrs.get('subject') or template.template_name
            attrs['body'] = attrs.get('body') or template.template_content

        if not attrs.get('subject'):
            raise serializers.ValidationError({"subject": "subject অথবা template — যেকোনো একটি নির্বাচন করতে হবে।"})
        if not attrs.get('body'):
            raise serializers.ValidationError({"body": "body অথবা template — যেকোনো একটি নির্বাচন করতে হবে।"})

        return attrs

    def create(self, validated_data):
        validated_data['sender'] = self.context['request'].user
        validated_data['folder'] = 'sent'
        return super().create(validated_data)
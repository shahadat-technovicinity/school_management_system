from django.core.mail import EmailMessage
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_via_smtp(mail_obj):
    """
    ১ জন হোক বা অনেকজন — সবাইকে BCC তে রেখে পাঠানো হয়,
    যাতে recipient রা একে অপরের email দেখতে না পায় (privacy)।
    """
    try:
        recipient_list = [e.strip() for e in mail_obj.to_emails.split(',') if e.strip()]

        if not recipient_list:
            mail_obj.smtp_error = "কোনো বৈধ প্রাপক (Recipient) পাওয়া যায়নি।"
            mail_obj.save(update_fields=['smtp_error'])
            return False

        email = EmailMessage(
            subject=mail_obj.subject,
            body=mail_obj.body,
            from_email=settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else settings.EMAIL_HOST_USER,
            to=[],  # To ফাঁকা রাখছি, সবাইকে BCC তে পাঠাচ্ছি
            bcc=recipient_list,
        )

        for attachment in mail_obj.attachments.all():
            if attachment.file:
                attachment.file.open('rb')
                email.attach(attachment.filename, attachment.file.read(), 'application/octet-stream')
                attachment.file.close()

        email.send(fail_silently=False)

        mail_obj.smtp_sent = True
        mail_obj.smtp_error = ""
        mail_obj.save(update_fields=['smtp_sent', 'smtp_error'])
        return True

    except Exception as e:
        logger.error(f"SMTP Error: {str(e)}")
        mail_obj.smtp_sent = False
        mail_obj.smtp_error = str(e)
        mail_obj.save(update_fields=['smtp_sent', 'smtp_error'])
        return False
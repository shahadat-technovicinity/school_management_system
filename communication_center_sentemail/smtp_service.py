from django.core.mail import EmailMessage
import logging

logger = logging.getLogger(__name__)

def send_via_smtp(mail_obj):
    """
    জ্যাঙ্গোর বিল্ট-ইন EmailMessage ব্যবহার করে জিমেইল SMTP-এর মাধ্যমে মেইল পাঠায়।
    """
    try:
        # কমা সেপারেটেড ইমেইলগুলোকে লিস্টে রূপান্তর
        recipient_list = [email.strip() for email in mail_obj.to_emails.split(',') if email.strip()]
        
        if not recipient_list:
            mail_obj.smtp_error = "কোনো বৈধ প্রাপক (Recipient) পাওয়া যায়নি।"
            mail_obj.save(update_fields=['smtp_error'])
            return False

        email = EmailMessage(
            subject=mail_obj.subject,
            body=mail_obj.body,
            from_email=None,  # settings.DEFAULT_FROM_EMAIL অটোমেটিক ব্যবহার হবে
            to=recipient_list,
        )

        # অ্যাটাচমেন্ট ফাইল যুক্ত করা
        for attachment in mail_obj.attachments.all():
            if attachment.file:
                email.attach(attachment.filename, attachment.file.read(), 'application/octet-stream')

        # মেইল সেন্ড করা
        email.send(fail_silently=False)
        
        # ডাটাবেজে স্ট্যাটাস আপডেট
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
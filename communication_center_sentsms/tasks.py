from celery import shared_task
from .models import SMSSentHistory
from .utils import send_sms


@shared_task
def send_bulk_sms_task(message, phone_numbers, group, template_id=None):
    result = send_sms(message, phone_numbers)

    sms_status = 'Success' if result.get('error') == 0 else 'Failed'
    SMSSentHistory.objects.create(
        template_id=template_id,
        message=message,
        recipients=','.join(phone_numbers),
        group=group,
        request_id=result.get('data', {}).get('request_id'),
        status=sms_status,
    )

    return result
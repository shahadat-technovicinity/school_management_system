import requests
from django.conf import settings


def send_sms(message, phone_numbers):
    valid_numbers = [n for n in phone_numbers if n]
    if not valid_numbers:
        return {'error': 416, 'msg': 'No valid number found'}

    to = ','.join(valid_numbers)

    response = requests.post(settings.SMS_API_ENDPOINT, data={
        'api_key': settings.SMS_API_KEY,
        'msg': message,
        'to': to,
    })
    return response.json()


def get_balance():
    response = requests.get(settings.SMS_BALANCE_ENDPOINT, params={
        'api_key': settings.SMS_API_KEY
    })
    return response.json()


def get_report(request_id):
    response = requests.get(
        f'{settings.SMS_REPORT_ENDPOINT}{request_id}/',
        params={'api_key': settings.SMS_API_KEY}
    )
    return response.json()
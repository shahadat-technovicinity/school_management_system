import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

SMS_NET_BD_SEND_URL = "https://api.sms.net.bd/sendsms"
SMS_NET_BD_BALANCE_URL = "https://api.sms.net.bd/user/balance/"


def format_bd_phone_number(phone_number):
    """নাম্বারকে 8801XXXXXXXXX ফরম্যাটে ক্লিন করে"""
    clean_phone = str(phone_number).strip().replace("+", "").replace("-", "").replace(" ", "")
    if clean_phone.startswith("01"):
        clean_phone = "88" + clean_phone
    elif clean_phone.startswith("1") and len(clean_phone) == 10:
        clean_phone = "880" + clean_phone
    return clean_phone


def send_sms_net_bd(recipients, message=None, content_id=None, sender_id=None, schedule=None):
    """sms.net.bd API দিয়ে মেসেজ সেন্ড করার ফাংশন"""
    api_key = getattr(settings, 'SMS_NET_BD_API_KEY', '')

    if not api_key:
        return False, {"error": 405, "msg": "API Key configured properly নয়"}

    if isinstance(recipients, (list, tuple, set)):
        formatted_numbers = [format_bd_phone_number(num) for num in recipients if num]
        to_param = ",".join(formatted_numbers)
    else:
        to_param = format_bd_phone_number(recipients)

    payload = {
        'api_key': api_key,
        'to': to_param
    }

    if message:
        payload['msg'] = message

    if content_id:
        payload['content_id'] = content_id

    if not message and not content_id:
        return False, {"error": 400, "msg": "মেসেজ টেক্সট অথবা Content ID দিতে হবে।"}

    if sender_id:
        payload['sender_id'] = sender_id
    elif hasattr(settings, 'SMS_NET_BD_SENDER_ID') and settings.SMS_NET_BD_SENDER_ID:
        payload['sender_id'] = settings.SMS_NET_BD_SENDER_ID

    if schedule:
        payload['schedule'] = schedule

    try:
        response = requests.post(SMS_NET_BD_SEND_URL, data=payload, timeout=15)
        res_data = response.json()

        if res_data.get('error') == 0:
            logger.info(f"SMS Success: Request ID {res_data.get('data', {}).get('request_id')}")
            return True, res_data
        else:
            return False, res_data

    except Exception as e:
        logger.exception(f"SMS Exception: {str(e)}")
        return False, {"error": 500, "msg": str(e)}


def check_sms_balance():
    """sms.net.bd একাউন্টের ব্যালেন্স চেক করার ফাংশন"""
    api_key = getattr(settings, 'SMS_NET_BD_API_KEY', '')
    try:
        response = requests.get(SMS_NET_BD_BALANCE_URL, params={'api_key': api_key}, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": 500, "msg": str(e)}
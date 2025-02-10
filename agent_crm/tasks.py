import requests
from django.conf import settings
from celery import shared_task


@shared_task
def send_whatsapp_message(whatsapp_number, message):
    url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.TWILIO_ACCOUNT_SID}/Messages.json"

    payload = {
        "To": f"whatsapp:{whatsapp_number}",
        "From": f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}",
        "Body": message,
    }

    headers = {
        "Authorization": f"Basic {settings.TWILIO_AUTH_TOKEN}",
    }

    response = requests.post(url, data=payload, headers=headers)
    return response.status_code

import logging

from celery import shared_task
from django.conf import settings
from twilio.rest import Client

logger = logging.getLogger(__name__)


@shared_task
def send_whatsapp_message(to, message):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    try:
        msg = client.messages.create(
            from_=f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}",
            body=message,
            to=f"whatsapp:{to}",
        )
        return msg.sid
    except Exception as e:
        error_message = f"Error sending WhatsApp message to {to}: {str(e)}"
        logger.error(error_message)
        return error_message

from twilio.rest import Client
from django.conf import settings

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
        return str(e)
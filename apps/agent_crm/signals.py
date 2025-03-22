import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

from services import send_whatsapp_message

from .models import Lead

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Lead)
def send_lead_notification(sender, instance, created, **kwargs):
    """
    Notify the assigned agent and send a confirmation email to the user
    when a new lead is created.
    """
    if created:
        logger.info(f"New Lead created: {instance.id}")
        agent = instance.assigned_agent
        if agent and agent.whatsapp_number:
            agent_whatsapp_message = f"New Lead Assignment: \n"
            agent_whatsapp_message += f"Buyer: {instance.buyer.first_name}\n"
            agent_whatsapp_message += f"Property: {instance.property}\n"
            agent_whatsapp_message += f"Message: {instance.message}\n"
            try:
                send_whatsapp_message(agent.whatsapp_number, agent_whatsapp_message)
                logger.info(f"WhatsApp message sent to agent {agent.whatsapp_number}")
            except Exception as e:
                logger.error(f"Error sending WhatsApp message to agent: {e}")

        buyer_phone = instance.buyer.whatsapp_number
        if buyer_phone:  # Ensure the buyer has a phone number
            buyer_whatsapp_message = f"Hello {instance.buyer.first_name},\n"
            buyer_whatsapp_message += (
                f"Your inquiry for {instance.property} has been received.\n"
            )
            buyer_whatsapp_message += f"Our agent wi ll contact you soon."
            try:
                send_whatsapp_message(buyer_phone, buyer_whatsapp_message)
                logger.info(f"WhatsApp message sent to buyer {buyer_phone}")
            except Exception as e:
                logger.error(f"Error sending WhatsApp message to buyer: {e}")

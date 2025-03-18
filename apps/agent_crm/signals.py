from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Lead
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from services import send_whatsapp_message



@receiver(post_save, sender=Lead)
def send_lead_notification(sender, instance, created, **kwargs):
    """
    Notify the assigned agent and send a confirmation email to the user
    when a new lead is created.
    """
    if created:
        agent = instance.assigned_agent
        if agent and agent.whatsapp_number:
            agent_whatsapp_message = f"New Lead Assignment: \n"
            agent_whatsapp_message += f"Buyer: {instance.buyer.first_name}\n"
            agent_whatsapp_message += f"Property: {instance.property}\n"
            agent_whatsapp_message += f"Message: {instance.message}\n"
            send_whatsapp_message(agent.whatsapp_number, agent_whatsapp_message)
        buyer_phone = instance.buyer.whatsapp_number
        if buyer_phone:  # Ensure the buyer has a phone number
            buyer_whatsapp_message = f"Hello {instance.buyer.first_name},\n"
            buyer_whatsapp_message += f"Your inquiry for {instance.property} has been received.\n"
            buyer_whatsapp_message += f"Our agent wi ll contact you soon."
            send_whatsapp_message(buyer_phone, buyer_whatsapp_message)

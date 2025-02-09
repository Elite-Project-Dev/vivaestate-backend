from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Lead
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings




@receiver(post_save, sender=Lead)
def send_lead_notification(sender, instance, created, **kwargs):
    """
    Notify the assigned agent and send a confirmation email to the user
    when a new lead is created.
    """
    if created:
        agent = instance.assigned_agent
        if agent and agent.email:
           agent_context = {
               "agent_name":  getattr(agent.agentprofile, "agency_name", "No Agency"),
               "lead_buyer": instance.buyer.first_name,
               "lead_property": instance.property,
               "lead_message": instance.message,
            }
           agent_subject="New Lead Assigned to You"
           agent_email_body = render_to_string("crm/agent_notification.html", agent_context)
           agent_email = EmailMessage(
               subject=agent_subject,
               body=agent_email_body,
               to=[agent.email],
               from_email=settings.DEFAULT_FROM_EMAIL,
           )
           agent_email.content_subtype = "html"
           agent_email.send()
        
        buyer_email = instance.buyer.email
        if buyer_email:
            user_context = {
                "buyer_name": instance.buyer.first_name,
                "property_name": instance.property,
                "message": instance.message,
            }
            user_subject = "Your Lead Submission Confirmation"
            user_email_body = render_to_string("crm/user_confirmation.html", user_context)
            user_email = EmailMessage(
                subject=user_subject,
                body=user_email_body,
                to=[buyer_email],
                from_email=settings.DEFAULT_FROM_EMAIL,
            )
            user_email.content_subtype = "html"
            user_email.send()
        
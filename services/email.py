import logging

from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.http import urlsafe_base64_encode
from django.core.validators import validate_email
from django.template import TemplateDoesNotExist
from smtplib import SMTPException

logger = logging.getLogger(__name__)

def send_email_task(subject, recipient_email, template_name, context):
    try:
        html_message = render_to_string(template_name, context)
        email = EmailMessage(
            subject=subject,
            body=html_message,
            to=[recipient_email],
            from_email=context["from_email"],
        )
        email.content_subtype = "html"
        email.send()
    except TemplateDoesNotExist as e:
        logger.error(f"Template not found: {template_name} — {str(e)}", exc_info=True)
        raise
    except SMTPException as e:
        logger.error(f"SMTP error sending email: {template_name} — {str(e)}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error sending email: {template_name} — {str(e)}", exc_info=True)
        raise

class EmailService:
    def __init__(self, default_sender=None):
        self.default_sender = default_sender or settings.DEFAULT_FROM_EMAIL

    def send_email(self, subject, recipient_email, template_name, context):
        validate_email(recipient_email)
        if not subject or not template_name:
            raise ValueError("Subject and template name are required")
        context["from_email"] = self.default_sender
        send_email_task(subject, recipient_email, template_name, context)
            

    def send_signup_verification_email(self, request, user_data):
        first_name = str(user_data["first_name"]).capitalize()
        verification_url = self.create_verification_url(request, user_data["email"])
        auth_code = get_random_string(length=6, allowed_chars="0123456789")

        cache.set(f"auth_code_{user_data['email']}", auth_code, timeout=900)
        cache.set(f"user_data_{user_data['email']}", user_data, timeout=900)

        context = {
            "first_name": first_name,
            "verification_url": verification_url,
            "auth_code": auth_code,
        }

        logger.info(f"Sending email to {user_data['email']} with auth code {auth_code}")
        self.send_email(
            subject="Naija Realtors Account Verification",
            recipient_email=user_data["email"],
            template_name="accounts/verification.html",
            context=context,
        )

    def create_verification_url(self, request, email):
        from django.core.signing import Signer

        singer = Signer()
        token = singer.sign(email)
        return f"http://{get_current_site(request).domain}{reverse('email-verify')}?token={token}"

    def send_password_reset_email(self, request, user_obj):
        uidb64 = urlsafe_base64_encode(str(user_obj).encode())
        token = PasswordResetTokenGenerator().make_token(user_obj)
        reset_code = get_random_string(length=6, allowed_chars="0123456789")
        cache.set(f"password_reset_code_{user_obj.email}", reset_code, timeout=900)
        reset_url = f"http://{get_current_site(request).domain}{reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})}"

        context = {"reset_url": reset_url, "reset_code": reset_code}
        self.send_email(
            subject="Reset Your Password",
            recipient_email=user_obj.email,
            template_name="accounts/password_reset.html",
            context=context,
        )

    def send_prospect_to_agent(self, request, property_id):
        """Notify the agent about the interested buyer"""
        user = request.user

        from apps.properties.models import Property

        try:
            property_obj = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return "Property not found"

        assigned_agent = property_obj.assigned_agent
        property_link = request.build_absolute_uri(property_obj.get_absolute_url())
        if not assigned_agent or not assigned_agent.email:
            return "Agent email not found"
        context = {
            "assigned_agent": assigned_agent.first_name,
            "interested_buyer": user.first_name,
            "property_link": property_link,
            "interested_buyer_whatsapp_no": (
                user.whatsapp_number if user.whatsapp_number else ""
            ),
        }
        self.send_email(
            subject="New Buyer Interest in Your Property",
            recipient_email=assigned_agent.email,
            template_name="social/interested_buyer.html",
            context=context,
        )

    def send_possible_deal(self, request, property_id):
        """Notify the buyer that the agent will reach out"""
        user = request.user
        from apps.properties.models import Property

        try:
            property_obj = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return "Property not found"
        assigned_agent = property_obj.assigned_agent
        property_link = request.build_absolute_uri(property_obj.get_absolute_url())
        if not user.email:
            return "User email not found"
        context = {
            "first_name": user.first_name,
            "property_title": property_obj.title,
            "agent_whatsapp_no": (
                assigned_agent.whatsapp_number
                if assigned_agent.whatsapp_number
                else "Not available"
            ),
            "agent_email": assigned_agent.email,
            "property_link": property_link,
        }
        self.send_email(
            subject="Interest Confirmed - Your Assigned Agent",
            recipient_email=user.email,
            template_name="social/interested_confirmed.html",
            context=context,
        )

    def send_agent_lead_notification(self, request, property_id):
        """Notify agent about the customer message on insterest of agent posted property"""
        user = request.user
        message = request.data.get("message", "No message provided")
        from apps.properties.models import Property

        try:
            property_obj = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return "Property not found"
        assigned_agent = (
            property_obj.assigned_agent if property_obj.assigned_agent else ""
        )
        property_link = request.build_absolute_uri(property_obj.get_absolute_url())
        context = {
            "insterested_buyer": user.first_name,
            "property_link": property_link,
            "buyer_message": message,
            "interested_buyer_whatsapp_no": (
                user.whatsapp_number if user.whatsapp_number else ""
            ),
        }
        self.send_email(
            subject="New Lead: Interest in Your Property",
            recipient_email=assigned_agent.email,
            template_name="crm/lead_notification.html",
            context=context,
        )

    def confirmation_of_sent_lead(self, request, property_id):
        """Notify customer about the sent lead to assigned agent"""
        user = request.user
        from apps.properties.models import Property

        try:
            property_obj = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return "Property not found"
        assigned_agent = property_obj.assigned_agent
        if not assigned_agent or not assigned_agent.email:
            return "Agent email not found"
        property_link = request.build_absolute_uri(property_obj.get_absolute_url())
        context = {
            "first_name": user.first_name,
            "assigned_agent": assigned_agent.first_name,
            "property_link": property_link,
            "agent_whatsapp_number": (
                assigned_agent.whatsapp_number if assigned_agent.whatsapp_number else ""
            ),
        }
        self.send_email(
            subject="Interest Confirmed - Your Assigned Agent",
            recipient_email=user.email,
            template_name="crm/send_lead.html",
            context=context,
        )

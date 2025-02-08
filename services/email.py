import logging
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

def send_email_task(subject, recipient_email, template_name, context):
    html_message = render_to_string(template_name, context)
    email = EmailMessage(
        subject=subject,
        body=html_message,
        to=[recipient_email],
        from_email=context["from_email"]
        )
    email.content_subtype="html"
    email.send()

class EmailService:
    def __init__(self, default_sender=None):
        self.default_sender = default_sender or settings.DEFAULT_FROM_EMAIL

    def send_email(self, subject, recipient_email, template_name, context):
        context["from_email"] = self.default_sender
        send_email_task(subject, recipient_email, template_name, context)

    def send_signup_verification_email(self, request, user):
        first_name = str(user.first_name).capitalize()
        verification_url = self.create_verification_url(request, user.email)
        context ={
            "first_name": first_name,
            "verification_url": verification_url
        }
        self.send_email(
            subject="Naija Realtors Account Verification",
            recipient_email=user.email,
            template_name="accounts/vefication.html",
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
        cache.set(
            f"password_reset_code_{user_obj.email}", reset_code, timeout=900
        )
        reset_url = f"http://{get_current_site(request).domain}{reverse('password-reset-confirm', kwargs={'uidb64': uidb64, 'token': token})}"

        context = {"reset_url": reset_url, "reset_code": reset_code}
        self.send_email(
            subject="Reset Your Password",
            recipient_email=user_obj.email,
            template_name="accounts/password_reset.html",
            context=context,
        )
        














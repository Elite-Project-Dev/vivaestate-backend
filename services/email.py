import random
import threading
from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.core.signing import Signer
from django.urls import reverse
from django.utils.html import format_html


class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        try:
            self.email.send()
        except Exception as e:
            print(f"Error sending email: {e}")


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data["email_subject"],
            body=data["email_body"],
            to=[data["to_email"]],
        )
        EmailThread(email).start()


def send_signup_verification_email(request, user_data, is_agent=False):
    auth_code = random.randint(100000, 999999) 

    username = user_data["username"]
    email = user_data["email"]

    cache.set(f"auth_code_{email}", auth_code, timeout=600)
    cache.set(f"user_data_{email}", user_data, timeout=600)

    signer = Signer()
    signed_data = signer.sign(email) 

    current_site = get_current_site(request).domain
    relative_link = reverse("email-verify")  

   
    absurl = f"http://{current_site}{relative_link}?token={signed_data}"

    email_body = format_html(
        """
        <p>Hi {},</p>
        <p>Thank you for signing up! Please verify your email by clicking the button below:</p>
        <a href="{}" style="
            display: inline-block;
            padding: 10px 20px;
            font-size: 16px;
            color: #fff;
            background-color: #28a745;
            text-decoration: none;
            border-radius: 5px;
        ">
            Verify Email
        </a>
        <p>Alternatively, you can use the authentication code below to verify your email:</p>
        <h3 style="color: #333;">{}</h3>
        <p>If you didn't sign up for this account, please ignore this email.</p>
        """,
        username,
        absurl,
        auth_code,
    )

    email_subject = "Verify your email and authentication code"
    email_message = EmailMessage(
        subject=email_subject,
        body=email_body,
        to=[email],
    )

    email_message.content_subtype = "html" 
    email_message.send()

    return True

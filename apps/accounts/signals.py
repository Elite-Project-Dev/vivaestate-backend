from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from allauth.account.signals import user_signed_up
from django.shortcuts import redirect

from apps.subscription.tasks import (
    assign_free_subscription,
)  # Use Celery task if async is needed

User = get_user_model()


@receiver(post_save, sender=User)
def assign_free_subscription_on_signup(sender, instance, created, **kwargs):
    if created:  # Ensure this runs only when a new user is created
        assign_free_subscription(instance)


@receiver(user_signed_up)
def populate_extra_fields(request, user, **kwargs):
    """This function runs when a user signup using Google it will redirect the user to collect addition details"""

    if not user.whatsapp_number and user.is_agent:
        # redirect to profile completion endpoint 
        return redirect('/auth/complete-signup')


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from apps.subscription.tasks import assign_free_subscription  # Use Celery task if async is needed

User = get_user_model()

@receiver(post_save, sender=User)
def assign_free_subscription_on_signup(sender, instance, created, **kwargs):
    if created:  # Ensure this runs only when a new user is created
        assign_free_subscription(instance)


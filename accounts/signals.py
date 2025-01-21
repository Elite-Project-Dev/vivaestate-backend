from django.db.models.signals import post_delete
from django.dispatch import receiver

from accounts.models import User
from app.models import AgentProfile


@receiver(post_delete, sender=User)
def cleanup_user_related_data(sender, instance, **kwargs):
    """
    Clean up related AgentProfile, Client, and Domain when a user is deleted.
    """
    try:
        agent_profile = AgentProfile.objects.get(user=instance)
        client = agent_profile.client

        # Delete AgentProfile and related Client/Domain
        agent_profile.delete()
        client.delete()  # Cascade deletes schema and domain
    except AgentProfile.DoesNotExist:
        pass

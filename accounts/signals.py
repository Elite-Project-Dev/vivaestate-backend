from django.db.models.signals import post_delete,  post_save
from django.dispatch import receiver
from django_tenants.utils import tenant_context
from accounts.models import User
from app.models import AgentProfile, Client


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

@receiver(post_save, sender=Client)
def auto_migrate(sender, instance, created, **kwargs):
    if created:
        with tenant_context(instance):
            from django.core.management import call_command
            call_command('migrate')  # This runs migrations for the tenant schema
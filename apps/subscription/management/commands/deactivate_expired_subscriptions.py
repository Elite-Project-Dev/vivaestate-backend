from django.core.management.base import BaseCommand
from django.utils.timezone import now

from subscription.models import Subscription


class Command(BaseCommand):
    help = 'Deactivate expired subscriptions'

    def handle(self, *args, **kwargs):
        expired_subscriptions = Subscription.objects.filter(
            status='active',
            end_date__lt=now()
        )
        for subscription in expired_subscriptions:
            subscription.status = 'inactive'
            subscription.save()
        self.stdout.write(self.style.SUCCESS(f"Successfully deactivated {expired_subscriptions.count()} expired subscriptions"))
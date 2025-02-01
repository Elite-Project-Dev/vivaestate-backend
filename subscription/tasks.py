from celery import shared_task
from django.utils.timezone import now
from subscription.models import Subscription
from celery.schedules import crontab

@shared_task
def deactivate_expired_subscriptions():
    expired_subscriptions = Subscription.objects.filter(
        status='active',
        end_date__lt=now()
    )

    for subscription in expired_subscriptions:
        subscription.status = 'inactive'
        subscription.save()


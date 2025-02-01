import logging
from celery import shared_task
from django.utils.timezone import now
from subscription.models import Subscription, SubscriptionPlan
from datetime import timedelta
from django.utils import timezone
logger = logging.getLogger(__name__)
@shared_task
def assign_free_subscription(user):
    if not user.is_agent: 
        logger.warning("User is not an agent, skipping free subscription.")
        return
    existing_subscription = Subscription.objects.filter(user=user).first()

    if existing_subscription:
        logger.info("User already has a subscription, skipping free subscription.")
        return
    # Ensure you have the Free plan already in your database
    try:
        free_plan = SubscriptionPlan.objects.get(name="Free Plan")
    except SubscriptionPlan.DoesNotExist:
        logger.error("Free Plan does not exist! Subscription not assigned.")
        return  
    flutterwave_subscription_id = free_plan.flutterwave_plan_id if free_plan.flutterwave_plan_id else ""

    start_date = timezone.now()
    end_date = start_date + timedelta(days=30)  # Free plan lasts for 1 month
    
    Subscription.objects.create(
        user=user,
        plan=free_plan,
        flutterwave_subscription_id=flutterwave_subscription_id,
        status="active",
        start_date=start_date,
        end_date=end_date,
    )
    logger.info(f"Assigned Free Plan to user {user.username}.")




@shared_task
def deactivate_expired_subscriptions():
    expired_subscriptions = Subscription.objects.filter(
        status='active',
        end_date__lt=now()
    )

    for subscription in expired_subscriptions:
        subscription.status = 'inactive'
        subscription.save()


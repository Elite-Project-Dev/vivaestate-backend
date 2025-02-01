from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drf_project.settings')

app = Celery('drf_project')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'deactivate-expired-subscriptions': {
        'task': 'subscription.tasks.deactivate_expired_subscriptions',
        'schedule': crontab(minute=0, hour=0),  # Run every midnight
    },
}
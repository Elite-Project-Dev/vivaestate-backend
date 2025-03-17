from __future__ import absolute_import, unicode_literals
import os
import ssl
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'drf_project.settings')

app = Celery('drf_project')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.update(
    broker_use_ssl={
        'ssl_cert_reqs': ssl.CERT_NONE  # or ssl.CERT_REQUIRED if you have certificates
    },
    redis_backend_use_ssl={
        'ssl_cert_reqs': ssl.CERT_NONE  # or ssl.CERT_REQUIRED if you have certificates
    },
    beat_schedule={
        'deactivate-expired-subscriptions': {
            'task': 'subscription.tasks.deactivate_expired_subscriptions',
            'schedule': crontab(minute=0, hour=0),  # Run every midnight
        },
    }
)

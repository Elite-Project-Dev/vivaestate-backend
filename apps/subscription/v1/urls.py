from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SubscriptionPlanViewSet, SubscriptionViewSet, flutterwave_webhook

router = DefaultRouter()
router.register(r"subscription-plans", SubscriptionPlanViewSet)
router.register(r"subscriptions", SubscriptionViewSet)

urlpatterns = [
    path("webhook/flutterwave/", flutterwave_webhook, name="flutterwave_webhook"),
    path("", include(router.urls)),
]

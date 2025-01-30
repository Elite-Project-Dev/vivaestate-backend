from django.conf import settings
from django.db import models

from accounts.models import Audit


class SubscriptionPlan(Audit):
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    interval = models.CharField(max_length=20, choices=[('monthly', 'Monthly'), ('yearly', 'Yearly')])
    duration = models.IntegerField()
    flutterwave_plan_id = models.CharField(max_length=100, blank=True, null=True) 

    def __str__(self):
        return self.name
    
class Subscription(Audit):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    flutterwave_subscription_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='active')
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.email} - {self.plan.name}"

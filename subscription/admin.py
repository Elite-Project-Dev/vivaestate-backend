from django.contrib import admin

from .models import Subscription, SubscriptionPlan


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'amount', 'interval', 'duration', 'flutterwave_plan_id')
    search_fields = ('name', 'flutterwave_plan_id')
    list_filter = ('interval',)
    ordering = ('name',)

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'status', 'start_date', 'end_date')
    search_fields = ('user__email', 'plan__name', 'flutterwave_subscription_id')
    list_filter = ('status', 'start_date', 'end_date')
    ordering = ('-start_date',)
    autocomplete_fields = ('user', 'plan')  # For a better experience with ForeignKey fields

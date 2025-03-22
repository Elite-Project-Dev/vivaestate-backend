from rest_framework import serializers

from .models import Subscription, SubscriptionPlan


class SubscriptionPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlan
        fields = ["id", "name", "amount", "interval", "duration", "flutterwave_plan_id"]
        read_only_fields = ["id", "flutterwave_plan_id"]

    def validate_amount(self, value):
        if value < 0:
            raise serializers.ValidationError("Amount cannot be negative.")
        return value


class SubscriptionSerializer(serializers.ModelSerializer):
    plan = serializers.PrimaryKeyRelatedField(
        queryset=SubscriptionPlan.objects.all()
    )  # Enables dropdown in DRF UI

    class Meta:
        model = Subscription
        fields = [
            "id",
            "user",
            "plan",
            "flutterwave_subscription_id",
            "status",
            "start_date",
            "end_date",
        ]
        read_only_fields = [
            "id",
            "flutterwave_subscription_id",
            "status",
            "start_date",
            "end_date",
        ]

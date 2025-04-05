import json
import uuid
from datetime import timedelta
from hashlib import sha512

import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from requests.exceptions import ConnectionError, RequestException, Timeout
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permission import IsAgent, IsSuperUser
from services import CustomResponseMixin

from ..models import Subscription, SubscriptionPlan
from .serializers import SubscriptionPlanSerializer, SubscriptionSerializer
from ..utils import create_payment_plan


class SubscriptionPlanViewSet(viewsets.ModelViewSet, CustomResponseMixin):
    """
    API endpoint for managing subscription plans.
    """

    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer
    permission_classes = [IsSuperUser, IsAuthenticated]

    @extend_schema(
        description="Create a new subscription plan and register it with Flutterwave.",
        responses={201: SubscriptionPlanSerializer()},
    )
    def perform_create(self, serializer):
        """
        Handles the creation of a subscription plan and integrates it with Flutterwave.
        """
        try:
            instance = serializer.save(commit=False)  # dont save yet
            plan_id = create_payment_plan(
                name=instance.name,
                amount=int(instance.amount),
                interval=instance.interval,
                duration=instance.duration,
            )
            if not plan_id:
               raise Exception("Failed to get plan ID from Flutterwave")

            instance.flutterwave_plan_id = plan_id
            instance.save()
        except ConnectionError:
            return self.custom_response(
                message="Failed to connect to Flutterwave API. Please check your internet connection.",
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except Timeout:
            return self.custom_response(
                message="Flutterwave API request timed out. Try again later.",
                status=status.HTTP_504_GATEWAY_TIMEOUT,
            )
        except RequestException as e:
            return self.custom_response(
                message=f"An error occurred: {str(e)}",
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return self.custom_response(
                message=f"Create Subscription Failed: {str(e)}",
                status=status.HTTP_400_BAD_REQUEST,
            )


class SubscriptionViewSet(viewsets.ModelViewSet, CustomResponseMixin):
    """
    API endpoint for managing subscriptions.
    """

    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated, IsAgent]

    @swagger_auto_schema(
        method="post",
        operation_description="Initiates a payment for a subscription plan.",
        responses={200: "Payment Link"},
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["plan_id"],
            properties={
                "plan_id": openapi.Schema(
                    type=openapi.TYPE_STRING, description="ID of the subscription plan"
                ),
            },
        ),
    )
    @action(detail=False, methods=["post"])
    def initiate_payment(self, request):
        """
        Initiates a subscription payment with Flutterwave.
        """
        user = request.user
        plan_id = request.data.get("plan_id")
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
            tx_ref = f"sub_{user.id}_{plan.id}_{uuid.uuid4()}"
            payment_data = {
                "tx_ref": tx_ref,
                "amount": int(plan.amount),
                "currency": "NGN",
                "payment_plan": plan.flutterwave_plan_id,
                "redirect_url": "http://localhost:8000/payment-callback",
                "customer": {"email": user.email},
            }
            response = requests.post(
                "https://api.flutterwave.com/v3/payments",
                json=payment_data,
                headers={
                    "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
                    "Content-Type": "application/json",
                },
            )
            if response.status_code in [200, 201]:
                return Response(
                    response.json().get("data", {}).get("link"),
                    status=status.HTTP_200_OK,
                )
            else:
                return self.custom_response(
                    message=f"Payment initiation failed: {response.json().get('message', 'Unknown error')}",
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except SubscriptionPlan.DoesNotExist:
            return self.custom_response(
                message="Plan not found", status=status.HTTP_404_NOT_FOUND
            )


@csrf_exempt
def flutterwave_webhook(request):  # it can be sent when it o local production
    """
    Webhook for handling payment updates from Flutterwave.
    """
    if request.method != "POST":
        return JsonResponse({"status": "error"}, status=400)

    if request.method == "POST":
        signature = request.headers.get("verif-hash")
        if (
            not signature
            or signature != sha512(settings.FLUTTERWAVE_SECRET_KEY.encode()).hexdigest()
        ):
            return JsonResponse({"status": "invalid signature"}, status=400)

        payload = json.loads(request.body)
        try:
            event = payload["event"]
            data = payload["data"]
            if event == "charge.completed":
                subscription_id = data["payment_plan"]
                tx_ref = data["tx_ref"]
                user_id, plan_id = tx_ref.split("_")[1:3]

                subscription, created = Subscription.objects.get_or_create(
                    user_id=user_id,
                    plan_id=plan_id,
                    flutterwave_subscription_id=subscription_id,
                    defaults={"status": "active"},
                )
                if created:
                    plan = subscription.plan
                    if plan.interval == "monthly":
                        subscription.end_date = subscription.start_date + timedelta(
                            days=30 * plan.duration
                        )
                    elif plan.interval == "yearly":
                        subscription.end_date = subscription.start_date + timedelta(
                            days=365 * plan.duration
                        )
                    subscription.save()

                return JsonResponse({"status": "success"})
        except (KeyError, IndexError, ValueError):
            return JsonResponse({"status": "invalid payload"}, status=400)

    return JsonResponse({"status": "error"}, status=400)

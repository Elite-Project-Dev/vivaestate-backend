import json
import uuid
from datetime import timedelta
from hashlib import sha512

import requests
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from services import CustomResponseMixin

from .models import Subscription, SubscriptionPlan
from .serializers import SubscriptionPlanSerializer, SubscriptionSerializer
from .utils import create_payment_plan


class SubscriptionPlanViewSet(viewsets.ModelViewSet):
    queryset = SubscriptionPlan.objects.all()
    serializer_class = SubscriptionPlanSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        # Create payment plan in Flutterwave
        plan_id = create_payment_plan(
            name=instance.name,
            amount=int(instance.amount * 100),
            interval=instance.interval,
            duration=instance.duration
        )
        instance.flutterwave_plan_id = plan_id
        instance.save()

class SubscriptionViewSet(viewsets.ModelViewSet, CustomResponseMixin):
    queryset = Subscription.objects.all()
    serializer_class = SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def initiate_payment(self, request):
        user = request.user
        plan_id = request.data.get('plan_id')
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
            tx_ref = f"sub_{user.id}_{plan.id}_{uuid.uuid4()}"
            # Initialize payment with Flutterwave
            payment_data = {
                "tx_ref": tx_ref,  # Unique reference
                "amount": int(plan.amount), 
                "currency": "NGN",
                "payment_plan": plan.flutterwave_plan_id,
                "redirect_url": "http://localhost:8000/payment-callback",
                "customer": {
                    "email": user.email,
                }
            }
            response = requests.post(
                "https://api.flutterwave.com/v3/payments",
                json=payment_data,
                headers={
                    "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
                    "Content-Type": "application/json",
                },)
            if response.status_code in [200, 201]:
                return Response(response.json().get('data', {}).get('link'), status=status.HTTP_200_OK)
            else:
                return self.custom_response(
                    message=f"Payment initiation failed: {response.json().get('message', 'Unknown error')}",
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except SubscriptionPlan.DoesNotExist:
            return self.custom_response(message="Plan not found", status=status.HTTP_404_NOT_FOUND)

@csrf_exempt
def flutterwave_webhook(request):
    if request.method == 'POST':
        signature = request.headers.get('verif-hash')
        if not signature or signature != sha512(settings.FLUTTERWAVE_SECRET_KEY.encode()).hexdigest():
            return JsonResponse({"status": "invalid signature"}, status=400)

        payload = json.loads(request.body)
        try:
            event = payload['event']
            data = payload['data']
            if event == 'charge.completed':
                subscription_id = data['payment_plan']
                tx_ref = data['tx_ref']
                user_id, plan_id = tx_ref.split('_')[1:3]
                subscription, created = Subscription.objects.get_or_create(
                    user_id=user_id,
                    plan_id=plan_id,
                    flutterwave_subscription_id=subscription_id,
                    defaults={"status": "active"}
                )
                if created:
                    plan = subscription.plan
                    if plan.interval == 'monthly':
                        subscription.end_date = subscription.start_date + timedelta(days=30 * plan.duration)  
                    elif plan.interval == 'yearly':
                        subscription.end_date = subscription.start_date + timedelta(days=365 * plan.duration) 
                    subscription.save()
                return JsonResponse({"status": "success"})
        except (KeyError, IndexError, ValueError):
            return JsonResponse({"status": "invalid payload"}, status=400)
    return JsonResponse({"status": "error"}, status=400)




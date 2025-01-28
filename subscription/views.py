from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import SubscriptionPlan, Subscription
from .serializers import SubscriptionPlanSerializer, SubscriptionSerializer
from .utils import create_payment_plan
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
from django.conf import settings
import requests
from services import CustomResponseMixin
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

    @action(detail=False, methods=['post'])
    def initiate_payment(self, request):
        user = request.user
        plan_id = request.data.get('plan_id')
        try:
            plan = SubscriptionPlan.objects.get(id=plan_id)
            # Initialize payment with Flutterwave
            payment_data = {
                "tx_ref": f"sub_{user.id}_{plan.id}",  # Unique reference
                "amount": int(plan.amount * 100),  # Convert to smallest currency unit
                "currency": "NGN",
                "payment_plan": plan.flutterwave_plan_id,
                "redirect_url": "https://yourwebsite.com/payment-callback",
                "customer": {
                    "email": user.email,
                }
            }
            # Make API request to Flutterwave
            url = "https://api.flutterwave.com/v3/payments"
            headers = {
                "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}", 
                "Content-Type": "application/json"
            }
            response = requests.post(url, json=payment_data, headers=headers)
            if response.status_code == 200:
                return Response(response.json()['data']['link'], status=status.HTTP_200_OK)
            else:
                return self.custom_response(message= "Failed to initiate payment", status=status.HTTP_400_BAD_REQUEST)
        except SubscriptionPlan.DoesNotExist:
            return self.custom_response(message= "Plan not found", status=status.HTTP_404_NOT_FOUND)
        
@csrf_exempt
def flutterwave_webhook(request):
    if request.method == 'POST':
        payload = json.loads(request.body)
        event = payload.get('event')
        data = payload.get('data')

        if event == 'charge.completed':
            subscription_id = data.get('payment_plan')
            tx_ref = data.get('tx_ref')
            user_id = tx_ref.split('_')[1]  # Extract user ID from tx_ref
            plan_id = tx_ref.split('_')[2]  # Extract plan ID from tx_ref

            # Create subscription record
            Subscription.objects.create(
                user_id=user_id,
                plan_id=plan_id,
                flutterwave_subscription_id=subscription_id,
                status='active'
            )

        return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)
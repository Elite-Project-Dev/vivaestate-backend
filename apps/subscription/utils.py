import requests
from django.conf import settings

FLUTTERWAVE_API_URL = "https://api.flutterwave.com/v3"

def create_payment_plan(name, amount, interval, duration):
    url = f"{FLUTTERWAVE_API_URL}/payment-plans"
    headers = {
        "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "amount": amount,
        "name": name,
        "interval": interval,
        "duration": duration
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()['data']['id']  # Return the plan ID
    else:
        raise Exception(f"Failed to create payment plan: {response.text}")
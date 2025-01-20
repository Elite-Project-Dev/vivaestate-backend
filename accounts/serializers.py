from rest_framework import serializers
from accounts.models import User
from datetime import date, timedelta
from django_tenants.utils import schema_context
from django.conf import settings
from app.models import Client, Domain, AgentProfile
from django.conf import settings
import re 

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'first_name', 'last_name']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        return user
    
class AgentSignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)
    agency_name=serializers.CharField(required=True, max_length=255)
    contact_info = serializers.CharField()
    class Meta:
        model = AgentProfile  # Link to the actual model that this serializer represents
        fields = ['email', 'username', 'password', 'first_name', 'last_name', 'agency_name', 'contact_info']
    def create(self, validated_data):
        user =  User.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        sanitized_username = re.sub(r'[^a-z0-9_]', '_', user.username.lower())

        trial_duration = getattr(settings, 'TRIAL_DURATION_DAYS', 90) 
        paid_until = date.today() + timedelta(days=trial_duration)
        client = Client.objects.create(
            name=validated_data['agency_name'],
            paid_until=paid_until,
            on_trial=True,
        )
        client.save()
        domain_name = settings.DOMAIN_NAME
        Domain.objects.create(
            domain=f"{sanitized_username}.{domain_name}",  # Example: unique subdomain
            tenant=client,
        )
        with schema_context(client.schema_name):
            AgentProfile.objects.create(
                client=client,
                user=user,
                agency_name=validated_data['agency_name'],
                contact_info=validated_data['contact_info'],
            )

        return user
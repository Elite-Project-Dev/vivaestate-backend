from rest_framework import serializers
from .models import  Lead

class LeadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lead
        fields = ['id', 'property', 'buyer', 'message', 'assigned_agent', 'status', 'created_at', 'last_updated']
        read_only_fields = ['id', 'assigned_agent', 'created_at', 'last_updated']

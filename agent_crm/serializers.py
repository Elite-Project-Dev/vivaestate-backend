from rest_framework import serializers
from .models import  Lead

class LeadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lead
        fields = ['id', 'property', 'buyer', 'message', 'assigned_agent', 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'assigned_agent', 'created_at', 'updated_at']
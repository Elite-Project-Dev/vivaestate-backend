from rest_framework import serializers
from .models import  Lead
from apps.properties.models import Property
class LeadSerializer(serializers.ModelSerializer):
    property = serializers.PrimaryKeyRelatedField(queryset=Property.objects.all(), required=True) 
    message=serializers.CharField(required=True, max_length=1000)
    class Meta:
        model = Lead
        fields = ['id', 'property', 'buyer', 'message', 'assigned_agent', 'status', 'created_at']
        read_only_fields = ['id', 'assigned_agent', 'created_at', 'buyer', 'status','created_at']
   
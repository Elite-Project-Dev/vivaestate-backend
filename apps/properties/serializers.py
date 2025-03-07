from rest_framework import serializers
from .models import Document, Property
from services import PROPERTY_TYPES, PROPERTY_STATUS_CHOICES
class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'property', 'document_type', 'file']

class PropertySerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(write_only=True, required=False)
    longitude = serializers.FloatField(write_only=True, required=False)
    location = serializers.SerializerMethodField()
    
    documents = DocumentSerializer(many=True, required=False)
    image = serializers.ImageField(required=False)
    video = serializers.FileField(required=False)
    bedrooms = serializers.CharField(required=False)
    bathrooms = serializers.CharField(required=False)
    square_feet = serializers.CharField(required=False)
    property_type = serializers.ChoiceField(choices=PROPERTY_TYPES)
    status=serializers.ChoiceField(choices=PROPERTY_STATUS_CHOICES)
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'price', 'description', 'property_type', 'bedrooms', 'bathrooms',
            'square_feet', 'status', 'image', 'video', 'documents', 'for_sale', 'for_rent',
            'latitude', 'longitude', 'location'
        ]
        
    def create(self, validated_data):
        return super().create(validated_data)
    
    def get_location(self, obj):
        return {"latitude": obj.latitude, "longitude": obj.longitude}

class UpdateLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ['latitude', 'longitude']
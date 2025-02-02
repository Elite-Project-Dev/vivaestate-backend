from rest_framework import serializers

from .models import  Document, Property, Location


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'property', 'document_type', 'file']
class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ['city', 'state', 'country']

class PropertySerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True,required=False)
    image = serializers.ImageField(required=False)
    video = serializers.FileField(required=False)
    bedrooms=serializers.CharField(required=False)
    bathrooms=serializers.CharField(required=False)
    square_feet=serializers.CharField(required=False)
    class Meta:
        model = Property
        fields = [
            'id', 'title', 'price', 'description', 'location', 'property_type', 'bedrooms', 'bathrooms',
            'square_feet', 'status', 'image', 'video', 'documents', 'for_sale', 'for_rent',
        ]


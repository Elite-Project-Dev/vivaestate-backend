from rest_framework import serializers

from .models import  Document, Property
from django.contrib.gis.geos import Point


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'property', 'document_type', 'file']


class PropertySerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(write_only=True, required=False)
    longitude = serializers.FloatField(write_only=True, required=False)
    location = serializers.SerializerMethodField()
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
            'square_feet', 'status', 'image', 'video', 'documents', 'for_sale', 'for_rent', 'latitude', 'longitude',
        ]
    
    def create(self, validated_data):
        lat = validated_data.pop('latitude', None)
        lng = validated_data.pop('longitude', None)
        if lat is not None and lng is not None:
            validated_data['location'] = Point(lng, lat)

        return super().create(validated_data)
    def get_location(self, obj):
        return {"latitude": obj.location.y, "longitude": obj.location.x}
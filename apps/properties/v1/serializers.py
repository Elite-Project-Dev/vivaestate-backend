from rest_framework import serializers

from services import PROPERTY_STATUS_CHOICES, PROPERTY_TYPES

from ..models import Document, Property


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "document_type", "file", "property"]


class PropertySerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(write_only=True, required=False)
    longitude = serializers.FloatField(write_only=True, required=False)
    location = serializers.SerializerMethodField()
    image = serializers.ImageField(required=False)
    video = serializers.FileField(required=False)
    bedrooms = serializers.CharField(required=False)
    bathrooms = serializers.CharField(required=False)
    square_feet = serializers.CharField(required=False)
    property_type = serializers.ChoiceField(choices=PROPERTY_TYPES)
    status = serializers.ChoiceField(choices=PROPERTY_STATUS_CHOICES)

    class Meta:
        model = Property
        fields = [
            "id",
            "title",
            "price",
            "description",
            "property_type",
            "bedrooms",
            "bathrooms",
            "square_feet",
            "status",
            "image",
            "video",
            "for_sale",
            "for_rent",
            "latitude",
            "longitude",
            "location",
        ]

    def get_location(self, obj):
        return {"latitude": obj.latitude, "longitude": obj.longitude}

from rest_framework import serializers

from services import PROPERTY_STATUS_CHOICES, PROPERTY_TYPES

from ..models import Document, Property, PropertyImage, PropertyVideo, PropertyLocation
from django.core.exceptions import ValidationError

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "document_type", "file", "property"]
    def validate(self, attrs):
        file = attrs.get("file")
        property_id = attrs.get("property")
        max_file_size_bytes = 100 * 1024 * 1024 # 100 MB
        if file.size > max_file_size_bytes:
            raise ValidationError(f"File size cannot exceed {max_file_size_bytes / (1024 * 1024)}MB.")
        try:
            Property.objects.get(pk=property_id)
        except Property.DoesNotExist:
            raise ValidationError("Invalid property ID.")
        return attrs 
class PropertyImageSerializer(serializers.ModelSerializer):
    images = serializers.ListField(
        child=serializers.ImageField(allow_empty_file=False,use_url=False)
    )
    class Meta:
        model=PropertyImage
        fields = ["id", "images", "property"]

        def validate(self, attrs):
            images = attrs.get("images")
            property_id = attrs.get("property")
            max_images = 10  # maximum number of image to be uploaded
            if len(images) > max_images:
                raise ValidationError(f"You can upload a maximum of {max_images} images.")
            max_image_size_bytes = 5 * 1024 * 1024  # max of 5mb
            for image in images:
                if image.size > max_image_size_bytes:
                    raise ValidationError({"image": "Image file size cannot exceed 5MB"})
            try:
                Property.objects.get(pk=property_id)
            except Property.DoesNotExist:
                raise ValidationError("Invalid property ID.")
            return attrs
        
class PropertyVideoSerializer(serializers.ModelSerializer):
    video = serializers.FileField(allow_empty_file=False, use_url=False)

    class Meta:
        model = PropertyVideo
        fields = ["id", "video", "property"]
    def validate(self, attrs):
        video = attrs.get("video")
        property_id = attrs.get("property")
        max_video_size_bytes = 100 * 1024 * 1024
        allowed_video_types = ['video/mp4', 'video/webm', 'video/ogg'] 
        if video.size > max_video_size_bytes:
            raise ValidationError(f"Video file size cannot exceed {max_video_size_bytes / (1024 * 1024)}MB.")

        if video.content_type not in allowed_video_types:
            raise ValidationError(f"Invalid video format. Allowed formats are: {', '.join(allowed_video_types)}.")
        try:
            Property.objects.get(pk=property_id)
        except Property.DoesNotExist:
            raise ValidationError("Invalid property ID.")
        return attrs 
class PropertySerializer(serializers.ModelSerializer):
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
            "for_sale",
            "for_rent",
        ]


class PropertyLocationSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(required=True)
    longitude =  serializers.FloatField(required=True)
    class Meta:
        model = PropertyLocation
        fields = ["latitude", "longitude", "property"]
    def validate_latitude(self, value):
        if not (-90 <= value <= 90):
            raise serializers.ValidationError("Latitude must be between -90 and 90 degrees.")
        return value
    def validate_longitude(self, value):
        if not (-180 <= value <= 180):
            raise serializers.ValidationError("Longitude must be between -180 and 180 degrees.")
        return value
    def validate_property(self, value):
        """
        Check if the provided property ID exists.
        """
        try:
            Property.objects.get(pk=value)
        except Property.DoesNotExist:
            raise ValidationError("Invalid property ID.")
        return value
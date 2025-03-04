from rest_framework import serializers


class BaseResponseSerializer(serializers.Serializer):
    """Base serializer for API responses."""
    status = serializers.CharField()
    message = serializers.CharField()
    metadata = serializers.DictField(required=False, default=dict)


class SuccessResponseSerializer(BaseResponseSerializer):
    """Standard success response serializer."""
    status = serializers.CharField(default="success")


class CreateResponseSerializer(BaseResponseSerializer):
    """Response for successfully created resources."""
    status = serializers.CharField(default="created")


class ErrorResponseSerializer(BaseResponseSerializer):
    """Base error response serializer."""
    status = serializers.CharField(default="failure")


class ErrorDataResponseSerializer(ErrorResponseSerializer):
    """Error response with additional data field."""
    data = serializers.DictField()


class NotFoundResponseSerializer(ErrorResponseSerializer):
    """Response for 404 Not Found errors."""
    status = serializers.CharField(default="not_found")
    message = serializers.CharField(default="The requested resource was not found.")

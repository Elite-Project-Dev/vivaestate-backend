from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from services import CustomResponseMixin, IsAgent, HasActiveSubscription
from .models import Property
from .serializers import PropertySerializer


class UpdateLocationView(APIView):
    permission_classes = [IsAuthenticated, IsAgent, HasActiveSubscription]
    def put(self, request, pk):
        try:
            property = Property.objects.get(pk=pk)
        except Property.DoesNotExist:
            return Response({"error": "Property not found"}, status=status.HTTP_404_NOT_FOUND)
        latitude = request.data.get('latitude')
        longitude = request.data.get('longitude')

        property.latitude = latitude
        property.longitude = longitude
        property.save()

        return Response({"message": "Location updated successfully"}, status=status.HTTP_200_OK)

class CustomResponseModelViewSet(CustomResponseMixin, viewsets.ModelViewSet):
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        return self.custom_response(
            message="Property fetched successfully",
            data=response.data,
            status=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return self.custom_response(
            status=status.HTTP_200_OK,
            message="Property fetched successfully",
            data=response.data,
        )

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return self.custom_response(
            status=status.HTTP_201_CREATED,
            message="Property created successfully",
            data=response.data,
        )

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response(
            status=status.HTTP_200_OK,
            message="Property updated successfully",
            data=response.data,
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response(
            status=status.HTTP_204_NO_CONTENT,
            message="Property deleted successfully",
        )


class PropertyViewSet(CustomResponseModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAgent, HasActiveSubscription]
        return [permission() for permission in permission_classes]

from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from services import CustomResponseMixin, IsAgent, HasActiveSubscription
from .models import Property
from .serializers import PropertySerializer
from django.utils import timezone
from datetime import timedelta
from rest_framework.decorators import action
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D  # Distance object

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
        return self.custom_response(
            status=status.HTTP_200_OK,
            message="Property updated successfully",
            data=response.data,
        )

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return self.custom_response(
            status=status.HTTP_204_NO_CONTENT,
            message="Property deleted successfully",
        )


class PropertyViewSet(CustomResponseModelViewSet):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at', 'square_feet']
    def get_permissions(self):
        if self.request.method == "GET":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAgent, HasActiveSubscription]
        return [permission() for permission in permission_classes]
    @action(detail=False, methods=['get'])
    def new_listings(self, request):
        recent = timezone.now() - timedelta(days=7)
        queryset = self.filter_queryset(self.get_queryset()).filter(created_at__gte=recent)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius = float(request.query_params.get('radius', 10))  # Default 10 km

        if not lat or not lng:
            return Response({"error": "Missing lat/lng parameters"}, status=status.HTTP_400_BAD_REQUEST)

        user_location = Point(float(lng), float(lat), srid=4326)  # Convert to geospatial Point
        nearby_properties = Property.objects.filter(location__distance_lte=(user_location, D(km=radius)))

        serializer = self.get_serializer(nearby_properties, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
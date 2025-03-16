import math
from datetime import timedelta

from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from drf_spectacular.utils import extend_schema, OpenApiParameter


from services import CustomResponseMixin
from apps.accounts.permission import  IsAgent, HasActiveSubscription
from .models import Property, Document
from .serializers import PropertySerializer, DocumentSerializer


class CustomResponseModelViewSet(CustomResponseMixin, viewsets.ModelViewSet):
    """ Custom response formatting for ViewSets """

    def list(self, request, *args, **kwargs):
        """ Retrieve a list of properties """
        response = super().list(request, *args, **kwargs)
        return self.custom_response(message="Properties fetched successfully", data=response.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        """ Retrieve a single property """
        response = super().retrieve(request, *args, **kwargs)
        return self.custom_response(status=status.HTTP_200_OK, message="Property fetched successfully", data=response.data)

    def create(self, request, *args, **kwargs):
        """ Create a new property """
        response = super().create(request, *args, **kwargs)
        return self.custom_response(status=status.HTTP_201_CREATED, message="Property created successfully", data=response.data)

    def update(self, request, *args, **kwargs):
        """ Update an existing property """
        response = super().update(request, *args, **kwargs)
        return self.custom_response(status=status.HTTP_200_OK, message="Property updated successfully", data=response.data)

    def destroy(self, request, *args, **kwargs):
        """ Delete a property """
        super().destroy(request, *args, **kwargs)
        return self.custom_response(status=status.HTTP_204_NO_CONTENT, message="Property deleted successfully")


### 🔹 Property ViewSet (Main API)
class PropertyViewSet(CustomResponseModelViewSet):
    """ ViewSet for managing property listings """

    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    search_fields = ['title', 'description']
    ordering_fields = ['price', 'created_at', 'square_feet']
    def get_permissions(self):
        """ Assign permissions based on request method """
        if self.request.method == "GET":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAgent, HasActiveSubscription]
        return [permission() for permission in permission_classes]

    @extend_schema(
        description="Retrieve properties listed in the last 7 days",
        responses={200: PropertySerializer(many=True)},
        request=PropertySerializer
    )
    @action(detail=False, methods=['get'])
    def new_listings(self, request):
        """ Returns properties listed in the last 7 days """
        recent = timezone.now() - timedelta(days=7)
        queryset = self.filter_queryset(self.get_queryset()).filter(created_at__gte=recent)
        serializer = self.get_serializer(queryset, many=True)
        return self.custom_response(data=serializer.data)

    @extend_schema(
        description="Find properties within a given radius based on latitude and longitude",
        parameters=[
            OpenApiParameter("lat", description="Latitude of the location", type=float),
            OpenApiParameter("lng", description="Longitude of the location", type=float),
            OpenApiParameter("radius", description="Search radius in km", type=float, default=10),
        ],
        responses={200: PropertySerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """ Find properties within a radius of given coordinates """
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')

        try:
            radius = float(request.query_params.get('radius', 10))  # Default 10 km
            lat = float(lat)
            lng = float(lng)
        except (TypeError, ValueError):
            return Response({"error": "Invalid or missing latitude, longitude, or radius parameters"}, status=status.HTTP_400_BAD_REQUEST)

        # Calculate lat/lng deltas
        lat_delta = radius / 111.0
        lng_delta = radius / (111.320 * math.cos(math.radians(lat)))

        # Filter properties within bounding box
        queryset = Property.objects.filter(
            latitude__gte=lat - lat_delta,
            latitude__lte=lat + lat_delta,
            longitude__gte=lng - lng_delta,
            longitude__lte=lng + lng_delta,
        )

        serializer = self.get_serializer(queryset, many=True)
        return self.custom_response(data=serializer.data, status=status.HTTP_200_OK)
    @action(detail=True, methods=['get'])
    def documents(self, request, pk=None):
        property = self.get_object()
        documents = property.documents.all()
        serializer = DocumentSerializer(documents, many=True)
        return self.custom_response(data=serializer.data) 
class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser)
    def get_permissions(self):
        """ Assign permissions based on request method """
        if self.request.method == "GET":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAgent, HasActiveSubscription]
        return [permission() for permission in permission_classes]

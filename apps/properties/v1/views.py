import math
from datetime import timedelta

from django.utils import timezone
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.accounts.permission import HasActiveSubscription, IsAgent
from services import CustomResponseMixin

from ..models import Document, Property, PropertyLocation , PropertyImage, PropertyVideo
from .serializers import DocumentSerializer, PropertySerializer , PropertyImageSerializer , PropertyVideoSerializer , PropertyLocationSerializer


class CustomResponseModelViewSet(CustomResponseMixin, viewsets.ModelViewSet):
    """Custom response formatting for ViewSets"""

    def list(self, request, *args, **kwargs):
        """Retrieve a list of properties"""
        response = super().list(request, *args, **kwargs)
        return self.custom_response(
            message="Properties data fetched successfully",
            data=response.data,
            status=status.HTTP_200_OK,
        )

    def retrieve(self, request, *args, **kwargs):
        """Retrieve a single property"""
        response = super().retrieve(request, *args, **kwargs)
        return self.custom_response(
            status=status.HTTP_200_OK,
            message="Property  data fetched successfully",
            data=response.data,
        )

    def create(self, request, *args, **kwargs):
        """Create a new property"""
        response = super().create(request, *args, **kwargs)
        return self.custom_response(
            status=status.HTTP_201_CREATED,
            message="Property data created successfully",
            data=response.data,
        )

    def update(self, request, *args, **kwargs):
        """Update an existing property"""
        response = super().update(request, *args, **kwargs)
        return self.custom_response(
            status=status.HTTP_200_OK,
            message="Property  data updated successfully",
            data=response.data,
        )

    def destroy(self, request, *args, **kwargs):
        """Delete a property"""
        super().destroy(request, *args, **kwargs)
        return self.custom_response(
            status=status.HTTP_204_NO_CONTENT, message="Property data deleted successfully"
        )


### 🔹 Property ViewSet (Main API)
class PropertyViewSet(CustomResponseModelViewSet):
    """ViewSet for managing property listings"""

    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    search_fields = ["title", "description"]
    ordering_fields = ["price", "created_at", "square_feet"]

    def get_permissions(self):
        """Assign permissions based on request method"""
        if self.action in ["list", "retrieve", "nearby"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAgent, HasActiveSubscription]
        return [permission() for permission in permission_classes]

    @extend_schema(
        description="Retrieve properties listed in the last 7 days",
        responses={200: PropertySerializer(many=True)},
        request=PropertySerializer,
    )
    @action(detail=False, methods=["get"])
    def new_listings(self, request):
        """Returns properties listed in the last 7 days"""
        recent = timezone.now() - timedelta(days=7)
        queryset = self.filter_queryset(self.get_queryset()).filter(
            created_at__gte=recent
        )
        serializer = self.get_serializer(queryset, many=True)
        return self.custom_response(data=serializer.data)

    @extend_schema(
        description="Find properties within a given radius based on latitude and longitude",
        parameters=[
            OpenApiParameter("lat", description="Latitude of the location", type=float),
            OpenApiParameter(
                "lng", description="Longitude of the location", type=float
            ),
            OpenApiParameter(
                "radius", description="Search radius in km", type=float, default=10
            ),
        ],
        responses={200: PropertySerializer(many=True)},
    )
    @action(detail=False, methods=["get"])
    def nearby(self, request):
        """Find properties within a radius of given coordinates"""
        lat = request.query_params.get("lat")
        lng = request.query_params.get("lng")

        try:
            radius = float(request.query_params.get("radius", 10))  # Default 10 km
            lat = float(lat)
            lng = float(lng)
        except (TypeError, ValueError):
            return Response(
                {
                    "error": "Invalid or missing latitude, longitude, or radius parameters"
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

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
    def perform_create(self, serializer):
        serializer.save(assigned_agent=self.request.user)


class DocumentViewSet(CustomResponseModelViewSet):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser)

    def get_permissions(self):
        """Assign permissions based on request method"""
        if self.request.method == "GET":
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAgent, HasActiveSubscription]
        return [permission() for permission in permission_classes]


class PropertyImageViewSet(CustomResponseModelViewSet):
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer
    def get_permission(self):
        "Assign permission based on request method"
        if self.action in ["list", "retrieve"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAgent, HasActiveSubscription]
        return [permission() for permission in permission_classes]
    def create(self , request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            images = serializer.validated_data.get('images')
            property_id = serializer.validated_data.get("property")
            created_images = []
            for image_file in images:
                property_image = PropertyImage.objects.create(property=property_id, image=image_file)
                created_images.append(property_image)
            response_serializer = self.get_serializer(created_images, many=True)
            return self.custom_response(data=response_serializer.data, status=status.HTTP_201_CREATED)
        return self.custom_response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PropertyVideoViewSet(CustomResponseModelViewSet):
    queryset = PropertyVideo.objects.all()
    serializer_class = PropertyVideoSerializer
    def get_permission(self):
        "Assign permission based on request method"
        if self.action in ["list", "retrieve"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAgent, HasActiveSubscription]
        return [permission() for permission in permission_classes]
class PropertyLocationViewSet(CustomResponseModelViewSet):
    queryset = PropertyLocation.objects.all()
    serializer_class =  PropertyLocationSerializer
    def get_permission(self):
        "Assign permission based on request method"
        if self.action in ["list", "retrieve"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated, IsAgent, HasActiveSubscription]
        return [permission() for permission in permission_classes]
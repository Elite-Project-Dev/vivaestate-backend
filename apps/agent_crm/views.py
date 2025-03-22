from drf_spectacular.utils import extend_schema
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import IsAuthenticated

from apps.properties.models import Property
from services import CustomResponseMixin, EmailService

from .models import Lead
from .serializers import LeadSerializer


class LeadViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
    CustomResponseMixin,
):
    """
    API endpoint for managing leads.
    """

    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "email", "phone", "status"]
    ordering_fields = ["created_at", "status"]

    @extend_schema(
        description="Retrieve a list of leads. Admins see all leads; agents see only assigned leads.",
        responses={200: LeadSerializer(many=True)},
    )
    def get_queryset(self):
        """
        Return leads based on the user's role.
        Admin users can see all leads, while agents only see assigned leads.
        """
        user = self.request.user
        if not user.is_authenticated:
            return Lead.objects.none()  # Return an empty queryset for anonymous users
        if getattr(user, "is_admin", False):
            return Lead.objects.all().order_by("-created_at")
        return Lead.objects.filter(assigned_agent=user).order_by("-created_at")

    @swagger_auto_schema(
        operation_description="Create a new lead and assign it to the authenticated agent.",
        responses={201: LeadSerializer()},
    )
    def create(self, request, *args, **kwargs):
        """Creates a new lead and sends notification emails."""

        # Extract property_id from request body
        property_id = request.data.get("property")
        message = request.data.get("message")
        # Validate if the property exists
        try:
            property_obj = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            return self.custom_response(
                message="Property not found.", status=status.HTTP_404_NOT_FOUND
            )
        #  Prepare lead data (use property_obj instead of ID)
        lead_data = {
            "property": property_obj.id,  # Store the ID, not object
            "buyer": request.user.id,  # Authenticated user
            "message": message,
        }
        #  Validate and save lead
        serializer = LeadSerializer(data=lead_data)
        if not serializer.is_valid():
            return self.custom_response(
                status=status.HTTP_400_BAD_REQUEST,
                message="Invalid data provided.",
                data=serializer.errors,
            )
        assigned_agent = property_obj.assigned_agent
        lead = serializer.save(buyer=request.user, assigned_agent=assigned_agent)

        #  Send email notifications (PASS PROPERTY ID, NOT OBJECT)
        try:
            email_service = EmailService()
            email_service.send_agent_lead_notification(request, property_id)  #  Fixed
            email_service.comfirmation_of_sent_lead(request, property_id)  #  Fixed
        except Exception as e:
            return self.custom_response(
                message=f"Failed to send email: {str(e)}",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return self.custom_response(
            message="Lead created successfully.",
            status=status.HTTP_201_CREATED,
            data=LeadSerializer(lead).data,
        )

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter, SearchFilter
from drf_yasg.utils import swagger_auto_schema
from drf_spectacular.utils import extend_schema
from .models import Lead
from .serializers import LeadSerializer
from services import EmailService, CustomResponseMixin
from rest_framework import status
from rest_framework import mixins, viewsets

class LeadViewSet(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet, CustomResponseMixin):
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
    def post(self, request, property_id):
        serializer = LeadSerializer
        if serializer.is_valid():
            try:
                property_id = int(property_id)
            except ValueError:
                return self.custom_response(message="Invalid property ID", status=status.HTTP_400_BAD_REQUEST)
            try:
                email_service = EmailService
                email_service.send_agent_lead_notification(request, property_id)
                email_service.comfirmation_of_sent_lead(request, property_id)
            except Exception as e:
                return self.custom_response(
                    message=f"Failed to send email: {str(e)}",
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
        return self.custom_response(
            status=status.HTTP_400_BAD_REQUEST,
            message="Invalid data provided.",
            data=serializer.errors,
        )
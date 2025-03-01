from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter, SearchFilter
from drf_yasg.utils import swagger_auto_schema
from drf_spectacular.utils import extend_schema
from .models import Lead
from .serializers import LeadSerializer


class LeadViewSet(viewsets.ModelViewSet):
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
        if getattr(user, "is_admin", False):
            return Lead.objects.all().order_by("-created_at")
        return Lead.objects.filter(assigned_agent=user).order_by("-created_at")

    @swagger_auto_schema(
        operation_description="Create a new lead and assign it to the authenticated agent.",
        responses={201: LeadSerializer()},
    )
    def perform_create(self, serializer):
        """
        Assign the currently authenticated user as the agent when creating a lead.
        """
        serializer.save(assigned_agent=self.request.user)

from django.utils.timezone import now
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.views import APIView

from app.models import AgentProfile
from services import CustomResponseMixin
from subscription.models import Subscription


class IsAgent(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            try:
                return AgentProfile.objects.filter(user=request.user).exists()
            except AgentProfile.DoesNotExist:
                return False
        return False
    
class HasActiveSubscription(BasePermission):
    """
    Allows access only to users with an active subscription.
    """

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False  # User is not logged in
        
        # Check if the user has an active subscription
        has_active_subscription = Subscription.objects.filter(
            user=user, 
            status='active', 
            end_date__gte=now()
        ).exists()
        
        return has_active_subscription

class SubscriptionProtectedView(APIView, CustomResponseMixin):
    """
    This view is only accessible to users with an active subscription.
    """
    permission_classes = [IsAuthenticated, HasActiveSubscription]

    def get(self, request):
        return self.custom_response(message= "You have access to this feature because you are subscribed!")
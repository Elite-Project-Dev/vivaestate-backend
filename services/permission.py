from django.utils.timezone import now
from rest_framework.permissions import BasePermission
from accounts.models import AgentProfile
from subscription.models import Subscription


class IsAdmin(BasePermission):
     def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_superuser)


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


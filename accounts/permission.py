from rest_framework.permissions import BasePermission
from app.models import AgentProfile



class IsAgent(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            try:
                return AgentProfile.objects.filter(user=request.user).exists()
            except AgentProfile.DoesNotExist:
                return False
        return False
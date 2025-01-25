from rest_framework.permissions import BasePermission
from app.models import Client



class IsAgent(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            try:
                return Client.objects.filter(user=request.user).exists()
            except Client.DoesNotExist:
                return False
        return False
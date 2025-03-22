from django.utils.timezone import now
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.permissions import BasePermission

from apps.subscription.models import Subscription


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            raise AuthenticationFailed("Authentication credentials were not provided.")
        return request.user.is_superuser


class IsAgent(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            raise AuthenticationFailed("You must be logged in to access this resource.")

        if not getattr(request.user, "is_agent", False):
            raise PermissionDenied(
                "You do not have permission to access this resource."
            )

        return True


class HasActiveSubscription(BasePermission):
    """
    Allows access only to users with an active subscription.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            raise AuthenticationFailed("You must be logged in to access this resource.")

        has_active_subscription = Subscription.objects.filter(
            user=request.user, status="active", end_date__gte=now()
        ).exists()

        if not has_active_subscription:
            raise PermissionDenied(
                "You need an active subscription to access this resource."
            )

        return True


class IsSuperUser(BasePermission):
    """
    Custom permission to allow access only to superusers.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            raise AuthenticationFailed(
                "You must be logged in to access this resource."
            )  # 401

        if not request.user.is_superuser:
            raise PermissionDenied(
                "You do not have permission to access this resource. Superuser access required."
            )  # 403

        return True

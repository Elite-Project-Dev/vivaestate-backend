from django.conf import settings
from django.db import models

from apps.accounts.models import AgentProfile, Audit
from apps.properties.models import Property


class Favourite(Audit):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    assigned_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_prospect",
    )

    class Meta:
        unique_together = (
            "user",
            "property",
        )  # Ensure a user can only like a property once


class Follow(Audit):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    agent = models.ForeignKey(AgentProfile, on_delete=models.CASCADE)

from django.conf import settings
from django.db import models

from apps.accounts.models import Audit
from apps.accounts.models import AgentProfile
from apps.properties.models import Property


class Favourite(Audit):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('user', 'property')  # Ensure a user can only like a property once

class Follow(Audit):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    agent = models.ForeignKey(AgentProfile, on_delete=models.CASCADE)
from django.conf import settings
from django.db import models


# Agent profile model that will be tenant-specific
class AgentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    agency_name = models.CharField(max_length=255, unique=True)
    contact_info = models.TextField()
    bio = models.TextField(blank=True)
    license_number = models.CharField(max_length=50, blank=True)
    address = models.CharField(max_length=255, blank=True)
    def __str__(self):
        return f"{self.agency_name} - {self.user.username}"


from django.db import models
from django.conf import settings
from services import LEAD_STATUS_CHOICES
from apps.properties.models import Property
from apps.accounts.models import Audit

class Lead(Audit):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='leads')
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='inquiries'
    )
    assigned_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_leads'
    )
    message = models.TextField()
    status = models.CharField(max_length=20, choices=LEAD_STATUS_CHOICES, default='new')

    def save(self, *args, **kwargs):
        # If no agent is explicitly assigned, default to the property's owner.
        if not self.assigned_agent and self.property and hasattr(self.property, 'owner'):
            self.assigned_agent = self.property.owner
        super().save(*args, **kwargs)

        
    def __str__(self):
        return f"Lead for {self.property} from {self.buyer if self.buyer else 'Anonymous'}"

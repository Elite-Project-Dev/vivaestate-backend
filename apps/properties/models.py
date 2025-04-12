from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse

from apps.accounts.models import Audit
from services import DOCUMENT_TYPE_CHOICES, PROPERTY_STATUS_CHOICES, PROPERTY_TYPES


def upload_property_documents(instance, filename):
    return f"properties/{instance.property.id}/documents/{filename}"


class Document(Audit):
    property = models.ForeignKey(
        "Property", on_delete=models.CASCADE, related_name="documents"
    )
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES,
    )
    file = models.FileField(upload_to=upload_property_documents, blank=True, null=True)

    def __str__(self):
        return f"{self.document_type} for {self.property.title}"




class Property(Audit):
    assigned_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_properties",
    )
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPES)
    description = models.TextField(blank=True, null=True)
    bedrooms = models.IntegerField(blank=True, null=True)
    bathrooms = models.IntegerField(blank=True, null=True)
    square_feet = models.IntegerField(blank=True, null=True)
    status = models.CharField(
        max_length=50, choices=PROPERTY_STATUS_CHOICES, default="available"
    )
    for_sale = models.BooleanField(default=False)
    for_rent = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def is_visible(self):
        """Checks if the agent has an active subscription"""
        # Assuming there's an 'agent' attribute related to this property
        return (
            self.user.subscription.active
            if hasattr(self, "agent") and hasattr(self.agent, "subscription")
            else False
        )

    def get_absolute_url(self):
        return reverse("property-detail", kwargs={"pk": self.pk})


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, related_name='property_image', on_delete=models.CASCADE )
    image = models.ImageField(upload_to="property_images/", blank=True, null=True)

    def __str__(self):
        return f"Image for{self.property.title}"
    
class PropertyVideo(models.Model):
    property = models.ForeignKey(Property, related_name='property_video', on_delete=models.CASCADE)
    image = models.ImageField(upload_to="property_videos/", blank=True, null=True)
    def __str__(self):
        return f"Video for{self.property.title}"
    
class PropertyLocation(models.Model):
    property = models.ForeignKey(Property, related_name='property_location', on_delete=models.CASCADE)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)],
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True,
        validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)],
    )
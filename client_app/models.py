from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from accounts.models import Audit
from services import DOCUMENT_TYPE_CHOICES, PROPERTY_STATUS_CHOICES, PROPERTY_TYPES



def upload_property_documents(instance, filename):
    return f"properties/{instance.property.id}/documents/{filename}"


class Document(Audit):
    property = models.ForeignKey('Property', on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(
        max_length=50,
        choices=DOCUMENT_TYPE_CHOICES,
    )
    file = models.FileField(upload_to=upload_property_documents, blank=True, null=True)


    
    def __str__(self):
        return f"{self.document_type} for {self.property.title}"
class Location(models.Model):
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    country = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.city}, {self.state}, {self.country}"

class Property(Audit):
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPES)
    description = models.TextField(blank=True, null=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    bedrooms = models.IntegerField(blank=True, null=True)
    bathrooms = models.IntegerField(blank=True, null=True)
    square_feet = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=PROPERTY_STATUS_CHOICES, default='available')
    image = models.ImageField(upload_to='property_images/', blank=True, null=True)
    video = models.FileField(upload_to='property_videos/', blank=True, null=True)
    document = models.FileField(upload_to='property_documents/', blank=True, null=True)
    for_sale = models.BooleanField(default=False)
    for_rent = models.BooleanField(default=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, validators=[MinValueValidator(-90.0), MaxValueValidator(90.0)])
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True, validators=[MinValueValidator(-180.0), MaxValueValidator(180.0)])
    def __str__(self):
        return self.title

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from accounts.models import Audit
from services import DOCUMENT_TYPE_CHOICES, PROPERTY_STATUS_CHOICES


class Category(Audit):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
class Subcategory(Audit):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('category', 'name')
    def __str__(self):
        return f"{self.name} (Under {self.category.name})"
    
  
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

class Property(Audit):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='properties',blank=True, null=True)
    sub_category = models.ForeignKey(Subcategory, on_delete=models.CASCADE,blank=True, null=True)
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255)
    property_type = models.CharField(max_length=50)  # E.g., 'Apartment', 'House', etc.
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

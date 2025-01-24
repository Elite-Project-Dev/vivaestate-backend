from django.db import models

class Property(models.Model):
    PROPERTY_STATUS_CHOICES = [
        ('available', 'Available'),
        ('sold', 'Sold'),
        ('under_negotiation', 'Under Negotiation'),
    ]
    
    title = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    location = models.CharField(max_length=255)
    property_type = models.CharField(max_length=50)  # E.g., 'Apartment', 'House', etc.
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    square_feet = models.IntegerField()
    status = models.CharField(max_length=50, choices=PROPERTY_STATUS_CHOICES, default='available')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

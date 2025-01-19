from django.db import models
from django_tenants.models import TenantMixin, DomainMixin

class Client(TenantMixin):
    name=models.CharField(max_length=100)
    created_on = models.DateField(auto_created=True)

class Domain(DomainMixin):
    pass

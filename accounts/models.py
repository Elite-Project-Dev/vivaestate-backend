from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models


class Audit(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser, Audit):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_agent = models.BooleanField(default=False)


class UserProfile(Audit):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(
        upload_to="profile_pictures/", blank=True, null=True
    )
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} Profile"


class UserRole(Audit):
    USER_ROLES = (
        ("Admin", "Admin"),
        ("Agent", "Agent"),
        ("Customer", "Customer"),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, choices=USER_ROLES)

    def __str__(self):
        return f"{self.user.email} - {self.role}"

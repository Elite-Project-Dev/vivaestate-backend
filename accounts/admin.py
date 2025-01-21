from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, UserProfile, UserRole


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone_number", "location", "updated_at")
    search_fields = ("user__email", "phone_number", "location")
    list_filter = ("updated_at",)
    ordering = ("-updated_at",)
    readonly_fields = ("updated_at",)


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ("user", "role")
    search_fields = ("user__email", "role")
    list_filter = ("role",)
    ordering = ("role",)


class UserAdmin(BaseUserAdmin):
    # Fields to display in the list view
    list_display = ("email", "first_name", "last_name", "is_active", "is_staff")
    list_filter = ("is_staff", "is_active", "is_superuser")

    # Fields to search for in the admin search bar
    search_fields = ("email", "first_name", "last_name")

    # Fields to include in the form for adding or changing users
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    # Fields for creating a new user
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                ),
            },
        ),
    )

    # Fields for ordering the list
    ordering = ("email",)


# Register the custom User model with the custom UserAdmin
admin.site.register(User, UserAdmin)

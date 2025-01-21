from django.contrib import admin

from .models import AgentProfile, Client, Domain


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "paid_until", "on_trial", "created_on", "schema_name")
    search_fields = ("name", "schema_name")
    list_filter = ("on_trial", "created_on")
    ordering = ("-created_on",)
    readonly_fields = ("created_on",)


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ("domain", "tenant", "is_primary")
    search_fields = ("domain",)
    list_filter = ("is_primary",)
    ordering = ("domain",)


@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
    list_display = ("agency_name", "user", "client", "license_number")
    search_fields = ("agency_name", "user__username", "license_number")
    list_filter = ("client",)
    ordering = ("agency_name",)

from django.contrib import admin

from .models import AgentProfile


@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
    list_display = ("agency_name", "user", "license_number")
    search_fields = ("agency_name", "user__username", "license_number")
    ordering = ("agency_name",)

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile, UserRole, AgentProfile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'is_agent', 'whatsapp_number', 'is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('id',)
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('is_agent', 'whatsapp_number')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('is_agent', 'whatsapp_number')}),
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'phone_number', 'location', 'updated_at')
    search_fields = ('user__email', 'phone_number', 'location')


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'role')
    search_fields = ('user__email', 'role')


@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'agency_name', 'license_number', 'address')
    search_fields = ('agency_name', 'user__email', 'license_number')

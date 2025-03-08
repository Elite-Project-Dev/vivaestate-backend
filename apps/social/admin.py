from django.contrib import admin
from .models import Favourite, Follow

@admin.register(Favourite)
class FavouriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'property', 'assigned_agent', 'created_at')
    search_fields = ('user__email', 'property__title', 'assigned_agent__email')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'agent', 'created_at')
    search_fields = ('user__email', 'agent__user__email')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

from django.contrib import admin
from .models import Property, Document

@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_agent', 'price', 'property_type', 'status', 'for_sale', 'for_rent')
    list_filter = ('property_type', 'status', 'for_sale', 'for_rent')
    search_fields = ('title', 'assigned_agent__email', 'assigned_agent__username')
    ordering = ('-id',)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('document_type', 'property', 'file')
    list_filter = ('document_type',)
    search_fields = ('property__title',)






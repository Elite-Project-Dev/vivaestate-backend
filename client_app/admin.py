from django.contrib import admin

from .models import Category, Document, Property, Subcategory


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'created_at',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(Subcategory)
class SubcategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'description', 'created_at',)
    search_fields = ('name', 'category__name')
    list_filter = ('category',)
    ordering = ('category', 'name')


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'sub_category', 'price', 'status', 'for_sale', 'for_rent', 'location', 'created_at',)
    search_fields = ('title', 'location', 'category__name', 'sub_category__name')
    list_filter = ('status', 'for_sale', 'for_rent', 'category', 'sub_category')
    ordering = ('-created_at',)
    fieldsets = (
        (None, {
            'fields': ('title', 'price', 'description', 'category', 'sub_category', 'status', 'location', 'latitude', 'longitude')
        }),
        ('Property Details', {
            'fields': ('property_type', 'bedrooms', 'bathrooms', 'square_feet', 'for_sale', 'for_rent')
        }),
        ('Media', {
            'fields': ('image', 'video', 'document')
        }),
    )


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('document_type', 'property', 'file', 'created_at',)
    search_fields = ('document_type', 'property__title')
    list_filter = ('document_type',)
    ordering = ('-created_at',)

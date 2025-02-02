import django_filters
from .models import Property
class PropertyFilter(django_filters.FilterSet):
    price_min = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    price_max = django_filters.NumberFilter(field_name='price', lookup_expr='lte')
    city = django_filters.CharFilter(field_name='location__city')
    state = django_filters.CharFilter(field_name='location__state')
    country = django_filters.CharFilter(field_name='location__country')
    bedrooms_min = django_filters.NumberFilter(field_name='bedrooms', lookup_expr='gte')
    bathrooms_min = django_filters.NumberFilter(field_name='bathrooms', lookup_expr='gte')
    bathrooms_min = django_filters.NumberFilter(field_name='bathrooms', lookup_expr='gte')
    square_feet_min = django_filters.NumberFilter(field_name='square_feet', lookup_expr='gte')

    class Meta:
        model = Property
        fields = {
            'property_type': ['exact'],
            'status': ['exact'],
            'for_sale': ['exact'],
            'for_rent': ['exact'],
        }

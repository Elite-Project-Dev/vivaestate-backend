from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework_nested import routers

from .views import PropertyViewSet

router = routers.SimpleRouter()
router.register("property", PropertyViewSet, basename="property")

urlpatterns = [
    path('properties/affordable/', PropertyViewSet.as_view({'get': 'list'}),
         {'price_max': 50000}),
    path('properties/luxury/', PropertyViewSet.as_view({'get': 'list'}),
         {'price_min': 500000}),
    path('properties/rentals/', PropertyViewSet.as_view({'get': 'list'}),
         {'for_rent': True}),
    path('properties/for-sale/', PropertyViewSet.as_view({'get': 'list'}),
         {'for_sale': True}),
    path("", include(router.urls)),
    path('properties/commercial/', PropertyViewSet.as_view({'get': 'list'}),
         {'property_type': 'commercial'}),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
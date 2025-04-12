from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework_nested import routers

from .views import DocumentViewSet, PropertyViewSet, PropertyImageViewSet, PropertyVideoViewSet, PropertyLocationViewSet

router = routers.SimpleRouter()
router.register("property", PropertyViewSet, basename="property")
router.register("documents", DocumentViewSet, basename="document")
router.register("property-location", PropertyLocationViewSet, basename="location")
router.register("property-image", PropertyImageViewSet, basename="image")
router.register("property-video", PropertyVideoViewSet, basename="video")
urlpatterns = [   
    path("", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

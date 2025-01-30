from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework_nested import routers

from .views import PropertyViewSet, UpdateLocationView

router = routers.SimpleRouter()
router.register("property", PropertyViewSet, basename="property")

urlpatterns = [
    path('api/properties/<int:pk>/update-location/', UpdateLocationView.as_view(), name='update-location'),
    path("", include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
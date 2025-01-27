from django.urls import path, include
from . import views
from rest_framework_nested import routers
from .views import FavouritePropertyView

router = routers.SimpleRouter()
router.register("favourite-property", views.FavouritePropertyView, basename="favourite-property")

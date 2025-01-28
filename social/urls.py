from django.urls import path, include
from .views import FavouritePropertyView


urlpatterns = [
    path('favourite-property/<int:property_id>/', FavouritePropertyView.as_view(), name='favourite-property'),
]

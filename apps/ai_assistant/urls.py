from django.urls import path
from .views import PropertyChatAPIView

urlpatterns = [
    path('api/properties/<int:property_id>/chat/', PropertyChatAPIView.as_view(), name='property-chat'),
]

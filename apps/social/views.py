from django.shortcuts import get_object_or_404
from rest_framework import status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.properties.models import Property
from services import CustomResponseMixin

from .models import Favourite
from .serializers import PropertySerializer


class FavouritePropertyView(APIView, CustomResponseMixin):
    permission_classes = [IsAuthenticated]
    def get_property(self, property_id):
        return get_object_or_404(Property.objects.select_related(), id=property_id)
    def post(self, request, property_id):
        user = request.user
        property = self.get_property(property_id)

        if Favourite.objects.filter(user=user, property=property).exists():
            return self.custom_response(message="You have already liked this property", status=status.HTTP_400_BAD_REQUEST)
        Favourite.objects.create(user=user, property=property)
        return self.custom_response(message="Property liked successfully.", status=status.HTTP_201_CREATED)
    
    def delete(self, request, property_id):
        user = request.user
        property = self.get_property(property_id)
        favourite = Favourite.objects.filter(user=user, property=property)
        if favourite.exists():
            favourite.delete()  # Deleting the liked property
            return self.custom_response(
                message="Like removed successfully", 
                status=status.HTTP_204_NO_CONTENT
            )
        else:
            return self.custom_response(
                message="Property was not liked.", 
                status=status.HTTP_400_BAD_REQUEST
            )
    def get(self, request):
        user = request.user
        favourite_properties = Favourite.objects.filter(user=user)
        properties = Property.objects.filter(id__in=[f.property.id for f in favourite_properties])
        serializer = PropertySerializer(properties, many=True)
        return self.custom_response(data= serializer.data,status=status.HTTP_200_OK, message="Favourite properties fetched successfully" )
from django.shortcuts import get_object_or_404
from rest_framework import status, views
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.properties.models import Property
from services import CustomResponseMixin

from .models import Favourite
from .serializers import PropertySerializer
from services import EmailService
from django.http import Http404

class FavouritePropertyView(APIView, CustomResponseMixin):
    permission_classes = [IsAuthenticated]
    def get_property(self, property_id):
        """Retrieve a property or return a 404 response if not found."""
        return get_object_or_404(Property.objects.select_related(), id=property_id)
    def post(self, request, property_id):
        user = request.user
        try:
            property_id = int(property_id)
        except ValueError:
            return self.custom_response(message="Invalid property ID", status=status.HTTP_400_BAD_REQUEST)

        property_obj = Property.objects.filter(id=property_id).first()
        if not property_obj:
           return self.custom_response(message="Property not found", status=status.HTTP_404_NOT_FOUND)

        if Favourite.objects.filter(user=user, property=property_obj).exists():
            return self.custom_response(message="You have already liked this property", status=status.HTTP_400_BAD_REQUEST)
        email_service = EmailService()
        try:
            email_service.send_prospect_to_agent(request, property_id)
            email_service.send_possible_deal(request, property_id)
        except Exception as e:
            return self.custom_response(
                message=f"Failed to send email: {str(e)}",
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        Favourite.objects.create(user=user, property=property_obj, assigned_agent=property_obj.assigned_agent)
        return self.custom_response(
            status=status.HTTP_201_CREATED,
            message="Property liked successfully, and emails sent"
        )
    def delete(self, request, property_id):
        user = request.user
        property_obj = self.get_property(property_id)
        favourite = Favourite.objects.filter(user=user, property=property_obj,  assigned_agent=property_obj.assigned_agent)
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
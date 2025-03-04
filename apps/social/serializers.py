from rest_framework import serializers

from .models import Property,Favourite


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = Property
        fields = ['id', 'name', 'location', 'price', 'description', 'image'] 

class FavouritePropertySerializer(serializers.ModelSerializer):
    """ Serializer for adding and removing favorite properties. """

    class Meta:
        model = Favourite
        fields = ['id', 'user', 'property']
        read_only_fields = ['id', 'user']
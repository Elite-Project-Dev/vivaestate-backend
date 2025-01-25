from rest_framework import serializers
from .models import Category, Subcategory, Document, Property

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model= Category
        fields = ['id', 'name', 'description']

class SubcategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True
    )
    class Meta:
        model = Subcategory
        fields = ['id', 'category', 'category_id', 'name', 'description']

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'property', 'document_type', 'file']

class PropertySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(), source='category', write_only=True,required=False
    )
    sub_category = SubcategorySerializer(read_only=True)
    sub_category_id = serializers.PrimaryKeyRelatedField(
        queryset=Subcategory.objects.all(), source='sub_category', write_only=True,required=False
    )
    documents = DocumentSerializer(many=True,required=False)
    image = serializers.ImageField(required=False)
    video = serializers.FileField(required=False)
    bedrooms=serializers.CharField(required=False)
    bathrooms=serializers.CharField(required=False)
    square_feet=serializers.CharField(required=False)
    class Meta:
        model = Property
        fields = [
            'id', 'category', 'category_id', 'sub_category', 'sub_category_id', 'title',
            'price', 'description', 'location', 'property_type', 'bedrooms', 'bathrooms',
            'square_feet', 'status', 'image', 'video', 'documents', 'for_sale', 'for_rent',
        ]


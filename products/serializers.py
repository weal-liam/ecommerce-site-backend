from rest_framework import serializers
from django.utils.text import slugify
from categories.models import Category
from reviews.models import Review
from reviews.serializers import ReviewSerializer
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source='category.name', allow_null=True, required=False)
    display_image = serializers.SerializerMethodField()
    reviews = ReviewSerializer(many=True, read_only=True)
    
    def get_display_image(self, obj):
        return obj.get_image()
        
    def validate(self, data):
        image = data.get('image')
        image_url = data.get('image_url')
        if not image and not image_url:
            raise serializers.ValidationError('You must at least provide either an image or image URL')
        return data
    
    def create(self, validated_data):
        # validated_data may contain a nested dict for dotted-source fields
        # e.g. {'category': {'name': 'audio'}} because `category` uses
        # source='category.name'. Extract and resolve/create the Category
        # instance explicitly before creating the Product.
        category_data = validated_data.pop('category', None)
        if category_data:
            if isinstance(category_data, dict):
                category_name = category_data.get('name')
            else:
                category_name = category_data

            if category_name:
                category, _ = Category.objects.get_or_create(
                    name=category_name,
                    defaults={'slug': slugify(category_name)}
                )
                validated_data['category'] = category

        # Create and return the Product instance
        return Product.objects.create(**validated_data)
    
    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'description',
            'price',
            'image',
            'image_url',
            'display_image',
            'is_in_stock',
            'category',
            'stock',
            'reviews',
        )
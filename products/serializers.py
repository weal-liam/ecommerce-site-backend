from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)
    image_url = serializers.URLField(required=False, allow_null=True)
    display_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = '__all__'
    
    def get_display_image(self, obj):
        return obj.get_image()
        
    def validate(self, data):
        image = data.get('image')
        image_url = data.get('image_url')
        if not image and not image_url:
            raise serializers.ValidationError('You must atleast provide either an image or image URL')
        return data
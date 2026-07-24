from rest_framework import serializers

from .models import ShippingOption


class ShippingOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingOption
        fields = ['id', 'name', 'price', 'estimated_days', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

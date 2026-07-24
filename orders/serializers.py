from decimal import Decimal

from rest_framework import serializers

from products.models import Product
from products.serializers import ProductSerializer
from shipping.models import ShippingOption
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(required=False, read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True
    )

    class Meta:
        model = OrderItem
        fields = ('id', 'product', 'product_id', 'quantity')


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, required=False)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)
    shipping_option = serializers.PrimaryKeyRelatedField(
        queryset=ShippingOption.objects.filter(is_active=True),
        required=False,
        allow_null=True,
    )
    shipping_options = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = (
            'id',
            'order_id',
            'status',
            'customer_name',
            'customer_email',
            'customer_phone',
            'shipping_address',
            'created_at',
            'total_price',
            'items',
            'shipping_option',
            'shipping_options',
        )
        read_only_fields = ['id', 'order_id', 'created_at', 'total_price', 'user']

    def validate(self, data):
        if getattr(self, 'instance', None) is None and not data.get('items'):
            raise serializers.ValidationError({'items': 'This field is required.'})
        return data

    def get_shipping_options(self, obj):
        return [
            {
                'id': option.id,
                'name': option.name,
                'price': str(option.price),
                'estimated_days': option.estimated_days,
            }
            for option in ShippingOption.objects.filter(is_active=True)
        ]

    def _calculate_total(self, items_data, shipping_option=None):
        total_price = Decimal('0.00')
        for item_data in items_data:
            total_price += item_data['product'].price * item_data['quantity']
        if shipping_option is not None:
            total_price += shipping_option.price
        return total_price

    def create(self, validated_data, user=None):
        items_data = validated_data.pop('items', None)
        shipping_option = validated_data.pop('shipping_option', None)
        validated_data['total_price'] = self._calculate_total(items_data, shipping_option)
        if shipping_option is not None:
            validated_data['shipping_option'] = shipping_option
        if user is not None:
            order = Order.objects.create(user=user, **validated_data)
        else:
            order = Order.objects.create(**validated_data)
        
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)

        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        shipping_option = validated_data.pop('shipping_option', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if shipping_option is not None:
            instance.shipping_option = shipping_option

        if items_data is not None:
            instance.items.all().delete()
            instance.total_price = self._calculate_total(items_data, shipping_option)
            for item_data in items_data:
                OrderItem.objects.create(order=instance, **item_data)

        instance.save()
        return instance

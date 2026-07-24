import logging
from rest_framework import status, viewsets
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import CartSerializer
from products.models import Product


class CartViewSet(viewsets.ViewSet):
    logger = logging.getLogger(__name__)
    def get_cart(self):
        user = self.request.user if self.request.user.is_authenticated else None
        session_key = self.request.headers.get('X-Session-Key') or None

        if session_key is None and user is None:
            if not self.request.session.session_key:
                self.request.session.save()
            session_key = self.request.session.session_key

        cart, created = Cart.objects.get_or_create(
            user=user if user else None,
            session_key=None if user else session_key
        )
        return cart

    def cart_detail(self, request):
        cart = self.get_cart()
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def add_item(self, request):
        cart = self.get_cart()
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        if not product_id:
            return Response({'error': 'product_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            return Response({'error': 'quantity must be an integer'}, status=status.HTTP_400_BAD_REQUEST)

        if quantity < 1:
            return Response({'error': 'quantity must be at least 1'}, status=status.HTTP_400_BAD_REQUEST)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        serializer = CartSerializer(cart)
        return Response(status=status.HTTP_200_OK) 

    def remove_item(self, request, pk=None):
        cart = self.get_cart()

        if pk is None:
            return Response({'error': 'item id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            item = CartItem.objects.get(pk=pk, cart=cart)
        except CartItem.DoesNotExist:
            return Response({'error': 'Cart item not found'}, status=status.HTTP_404_NOT_FOUND)

        item.delete()
        serializer = CartSerializer(cart)
        return Response(status=status.HTTP_200_OK) 




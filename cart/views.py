from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
from django.shortcuts import get_object_or_404

class CartViewSet(viewsets.ViewSet):

    def get_cart(self, request):
        user = request.user if request.user.is_authenticated else None
        session_key = request.headers.get('X-Session-Key') or None

        if session_key is None and user is None:
            if not request.session.session_key:
                request.session.save()
            session_key = request.session.session_key


        cart, created = Cart.objects.get_or_create(
            user=user if user else None,
            session_key=None if user else session_key
        )
        return cart

    def list(self, request):
        cart = self.get_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart = self.get_cart(request)
        product_id = request.data.get('product_id')
        quantity = request.data.get('quantity', 1)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product_id=product_id,
            defaults={'quantity': quantity}
        )
        if not created:
            item.quantity += int(quantity)
            item.save()

        return Response({'message': 'Item added to cart.'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['delete'])
    def remove_item(self, request, pk=None):
        if pk is None:
            CartItem.objects.all().delete()
            return Response({'message':'items cleared'},status=status.HTTP_204_NO_CONTENT)
        cart = self.get_cart(request)
        item  = get_object_or_404(CartItem, pk=pk, cart=cart)
        item.delete()
        return Response({'message': 'Item removed.'},status=status.HTTP_204_NO_CONTENT)








import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.apps import apps

from cart.models import Cart

from .models import Order, OrderItem
from .serializers import OrderSerializer

Cart = apps.get_model('cart', 'Cart')
CartItem = apps.get_model('cart', 'CartItem')

class OrdersViewSet(viewsets.ViewSet):
    def list(self, request):
        max_no = request.query_params.get('max')
        min_no = request.query_params.get('min')
        date = request.query_params.get('date')

        orders = Order.objects.all().order_by('-created_at')

        if max_no:
            orders = orders.filter(id__lte=max_no)
        if min_no:
            orders = orders.filter(id__gte=min_no)
        if date:
            orders = orders.filter(created_at=date)
        
        my_orders = orders.filter(customer_name__icontains=request.user.username)
        serializer = OrderSerializer(orders, many=True)
        second_serializer = OrderSerializer(my_orders, many=True)
        
        if request.user.is_authenticated and not request.user.is_admin:
            return Response({'my_orders':second_serializer.data}, status=status.HTTP_200_OK)
        elif request.user.is_authenticated and request.user.is_admin:
            return Response({'total_orders' : serializer.data, 'my_orders': second_serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({'my_orders' :[]}, status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        return self.put(request, pk)


    def delete(self, request, pk):
        try:
            order = Order.objects.get(pk=pk)
            order.delete()
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': 'Deleted Successfully'}, status=status.HTTP_204_NO_CONTENT)


class CheckoutView(APIView):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    @csrf_exempt
    def post(self, request):
        user = request.user if request.user.is_authenticated else None

        # Get cart by user or session_key (as discussed previously)
        if user:
            cart = Cart.objects.filter(user=user).first()
        else:
            session_key = request.session.session_key if not\
                            request.headers.get('X-Session-Key') else\
                                 request.headers.get('X-Session-Key')
            if not session_key:
                request.session.save()
                session_key = request.session.session_key
            cart = Cart.objects.filter(session_key=session_key).first()

        if not cart or not cart.items.exists():
            return Response({'error': 'Cart is empty.'}, status=status.HTTP_400_BAD_REQUEST)

        # Optionally collect customer info from request.data for guests
        customer_name = user.get_full_name() if user else request.data.get('customer_name')
        customer_email = user.email if user else request.data.get('customer_email')
        customer_phone = request.data.get('customer_phone')
        shipping_address = request.data.get('shipping_address')
        total = request.data.get('total')
        line_items = []

        order = Order.objects.create(
            customer_name=customer_name,
            customer_email=customer_email,
            customer_phone=customer_phone,
            shipping_address=shipping_address,
            total_price=total
        )

        for cart_item in cart.items.all():
            line_items.append({
                'price_data':{
                    'currency':'usd',
                    'product_data':{
                        'name': cart_item.product.name
                    },
                    'unit_amount': int(float(cart_item.product.price) * 100)
                },
                'quantity': cart_item.quantity
            })

            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price_at_order=cart_item.product.price
            )

        order.save()

        domain = settings.CORS_ALLOWED_ORIGINS[0]
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items= line_items,
            mode='payment',
            metadata={'session_key':session_key,'order_id': order.id} if not\
                request.user.is_authenticated else {'user': request.user, 'order_id': order.id},
            success_url=f'{domain}/mart/cart?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{domain}/mart/cart?session_id={{CHECKOUT_SESSION_ID}}'
        )

        cart.items.all().delete()  # Optionally clear cart

        serializer = OrderSerializer(order)
        return Response({'order':serializer.data,'id':checkout_session.id}, status=status.HTTP_201_CREATED)
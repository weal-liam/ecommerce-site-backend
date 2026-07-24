import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.db import transaction
from django.core.cache import cache


from cart.models import Cart

from .models import Order
from .serializers import OrderSerializer
from payments.services import create_checkout_session

class IsAdmin(IsAuthenticated):
    """Permission check for admin users"""
    def has_permission(self, request, view):
        return super().has_permission(request, view) and getattr(request.user, 'is_admin', False)


class AdminOrdersListAPIView(generics.ListAPIView):
    """Admin endpoint to retrieve all orders"""
    queryset = Order.objects.prefetch_related('items__product').order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        queryset = super().get_queryset()
        max_no = self.request.query_params.get('max')
        min_no = self.request.query_params.get('min')
        date = self.request.query_params.get('date')

        if max_no:
            queryset = queryset.filter(id__lte=max_no)
        if min_no:
            queryset = queryset.filter(id__gte=min_no)
        if date:
            queryset = queryset.filter(created_at=date)

        return queryset


class CustomerOrdersListAPIView(generics.ListCreateAPIView):
    """Customer endpoint to retrieve only their own orders and create new ones"""
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return only orders belonging to the current user"""
        queryset = Order.objects.prefetch_related('items__product').filter(
            user=self.request.user
        ).order_by('-created_at')

        max_no = self.request.query_params.get('max')
        min_no = self.request.query_params.get('min')
        date = self.request.query_params.get('date')

        if max_no:
            queryset = queryset.filter(id__lte=max_no)
        if min_no:
            queryset = queryset.filter(id__gte=min_no)
        if date:
            queryset = queryset.filter(created_at=date)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class OrdersListCreateAPIView(generics.ListCreateAPIView):
    queryset = Order.objects.prefetch_related('items__product').order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class OrdersRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Order.objects.prefetch_related('items__product').order_by('-created_at')
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CheckoutView(APIView):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    @csrf_exempt
    def post(self, request):
        user = request.user if request.user.is_authenticated else None
        session_key = request.session.session_key if not\
                            request.headers.get('X-Session-Key') else\
                                 request.headers.get('X-Session-Key')
        if not session_key:
                request.session.save()
                session_key = request.session.session_key

        # Optionally collect customer info from request.data for guests
        customer_name = user.get_full_name() if user else request.data.get('customer_name')
        customer_email = user.email if user else request.data.get('customer_email')
        customer_phone = request.data.get('customer_phone')
        shipping_address = request.data.get('shipping_address')

        # Build items payload for serializer and stripe line_items
        cart_items = request.data.get('items', [])
        items_payload = []
        line_items = []
        for ci in cart_items:
            items_payload.append({'product_id': ci['product']['id'], 'quantity': ci['quantity']})
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {'name': ci['product']['name']},
                    'unit_amount': int(float(ci['product']['price']) * 100)
                },
                'quantity': ci['quantity']
            })

        payload = {
            'customer_name': customer_name,
            'customer_email': customer_email,
            'customer_phone': customer_phone,
            'shipping_address': shipping_address,
            'items': items_payload,
        }

        # Idempotency: prefer explicit header, fallback to session key
        idem_key = request.headers.get('Idempotency-Key') or session_key
        cache_key = f'checkout:{idem_key}' if idem_key else None
        if cache_key:
            cached = cache.get(cache_key)
            if cached:
                logger.info('Idempotent checkout hit for key=%s', idem_key)
                # Return previously created order + session id
                try:
                    existing_order = Order.objects.get(pk=cached['order_id'])
                    serializer = OrderSerializer(existing_order)
                    return Response({'order': serializer.data, 'id': cached['session_id']}, status=status.HTTP_200_OK)
                except Order.DoesNotExist:
                    cache.delete(cache_key)

        try:
            serializer = OrderSerializer(data=payload)
            serializer.is_valid(raise_exception=True)

            with transaction.atomic():
                order = serializer.save(customer_name=customer_name)

                domain = settings.CORS_ALLOWED_ORIGINS[0]
                # Create stripe session via service helper
                checkout_session = create_checkout_session(
                    line_items=line_items,
                    metadata={'session_key': session_key, 'order_id': order.id} if not user else {'user_id': user.id, 'order_id': order.id},
                    success_url=f'{domain}/mart/cart?session_id={{CHECKOUT_SESSION_ID}}',
                    cancel_url=f'{domain}/mart/cart?session_id={{CHECKOUT_SESSION_ID}}'
                )

                # store idempotency mapping for short period
                if cache_key:
                    cache.set(cache_key, {'order_id': order.id, 'session_id': checkout_session.id}, timeout=60 * 60)

                # clear cart
                Cart.objects.filter(user=user).first().items.all().delete() or Cart.objects.filter(session_key=session_key).first().items.all().delete()

        except stripe.error.StripeError as e:
            logger.exception('Stripe error during checkout: %s', e)
            return Response({'error': 'Payment gateway error'}, status=status.HTTP_502_BAD_GATEWAY)
        except Exception as e:
            logger.exception('Error during checkout: %s', e)
            return Response({'error': 'Server error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = OrderSerializer(order)
        return Response({'order': serializer.data, 'id': checkout_session.id}, status=status.HTTP_201_CREATED)
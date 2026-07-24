import logging
from decimal import Decimal

from django.conf import settings
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
import stripe
from orders.models import Order
from payments.models import Payment
from payments.serializers import PaymentSerializer

logger = logging.getLogger(__name__)


class PaymentViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def confirm_order(self, request):
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response({'error': 'Session ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            session = stripe.checkout.Session.retrieve(session_id)
        except stripe.error.InvalidRequestError as exc:
            return Response({'error': 'Invalid session ID', 'details': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        except stripe.error.StripeError as exc:
            return Response({'error': 'Payment gateway error', 'details': str(exc)}, status=status.HTTP_502_BAD_GATEWAY)

        if session.payment_status != 'paid':
            return Response({'status': session.payment_status}, status=status.HTTP_402_PAYMENT_REQUIRED)

        owner = request.user.username if request.user.is_authenticated else session.metadata.get('session_key') or 'guest'
        amount = Decimal(session.amount_total) / Decimal(100)

        payment, created = Payment.objects.get_or_create(
            session_id=session_id,
            defaults={
                'owner': owner,
                'status': session.payment_status,
                'amount': amount,
            }
        )

        if not created:
            updated = False
            if payment.status != session.payment_status:
                payment.status = session.payment_status
                updated = True
            if payment.amount != amount:
                payment.amount = amount
                updated = True
            if payment.owner != owner:
                payment.owner = owner
                updated = True
            if updated:
                payment.save(update_fields=['owner', 'status', 'amount'])
        order = Order.objects.filter(id=session.metadata['order_id']).first()
        order.status = Order.Status.CONFIRMED
        order.save(update_fields=['status'])

        return Response({
            'status': payment.status,
            'payment': PaymentSerializer(payment).data,
            'order_id': session.metadata['order_id'],
        }, status=status.HTTP_200_OK)

    def list(self, request):
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)

        if getattr(request.user, 'is_admin', False):
            payments = Payment.objects.all()
            serializer = PaymentSerializer(payments, many=True)
            return Response({'total_payments': serializer.data}, status=status.HTTP_200_OK)

        payments = Payment.objects.filter(owner=request.user.username)
        serializer = PaymentSerializer(payments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

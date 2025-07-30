from datetime import datetime 

from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.response import Response
import stripe

from payments.models import Payment
from payments.serializers import PaymentSerializer


# Create your views here.
class PaymentViewSet(viewsets.ViewSet):
    def confirm_order(self, request):
        session_id = request.query_params.get('session_id')
        if not session_id:
            return Response({'error': 'Session ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == 'paid':
            serializer = PaymentSerializer(data={
                    'session_id':session_id,
                    'owner':request.user.username if request.user.is_authenticated\
                                                    else session.metadata.get('session_key'),
                    'status':session.payment_status,
                    'amount':session.amount_total,
                    })
            if serializer.is_valid():
                serializer.save()
            return Response({'status': session.payment_status,'payment': serializer.data,'order_id':session.metadata.get('order_id'),'err':serializer.errors}, status=status.HTTP_200_OK)
        else:
            return Response({'status': session.payment_status}, status=status.HTTP_402_PAYMENT_REQUIRED)

    def list(self, request):
        payments = Payment.objects.all()
        my_payments = payments.filter(owner__icontains=request.user.username)
        serializer = PaymentSerializer(my_payments,many=True)
        second_serializer = PaymentSerializer(payments,many=True)
        if request.user.is_authenticated and request.user.is_admin:
            return Response({'Total Payments':second_serializer.data,'My Payments':serializer.data},status=status.HTTP_200_OK)
        else:
            return Response(serializer.data,status=status.HTTP_200_OK)

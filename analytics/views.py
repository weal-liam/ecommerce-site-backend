from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from cart.models import Cart
from orders.models import OrderItem, Order
from payments.models import Payment
from products.models import Product
from django.db.models import Sum, F, FloatField
from django.contrib.auth import get_user_model
from django.utils.timezone import now, timedelta


class SalesStatsView(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        if request.user.is_admin:
            admin_data = self.get_admin_data()
            customer_data = self.get_customer_data(request.user)
            return Response({'admin_data': admin_data, 'customer_data': customer_data}, status=status.HTTP_200_OK)

        customer_data = self.get_customer_data(request.user)
        return Response({'customer_data': customer_data}, status=status.HTTP_200_OK)

    def get_admin_data(self):
        past_week = now() - timedelta(days=7)

        revenue = OrderItem.objects.filter(order__created_at__gte=past_week).aggregate(
            total=Sum(F('price_at_order') * F('quantity'), output_field=FloatField())
        )['total'] or 0

        top_products = list(OrderItem.objects
            .values('product__id', 'product__name')
            .annotate(total_sold=Sum('quantity'))
            .order_by('-total_sold')[:5])

        total_stock = Product.objects.aggregate(total=Sum('stock'))['total'] or 0
        customers = get_user_model().objects.filter(is_customer=True).count() or 0
        visitors = Cart.objects.count() or 0
        payments_made = Payment.objects.count() or 0

        orders = Order.objects.all()
        return {
            'revenue(last 7 days)': revenue,
            'top products': top_products,
            'total stock': total_stock,
            'customers': customers,
            'visitors': visitors,
            'paid orders': orders.filter(status="paid").count() or 0,
            'pending orders': orders.filter(status="pending").count() or 0,
            'cancelled orders': orders.filter(status="cancelled").count() or 0,
            'payments made': payments_made,
            'order count': orders.count() or 0,
        }

    def get_customer_data(self, user):
        user_orders = Order.objects.filter(customer_name__icontains=user.first_name)
        expenditure = OrderItem.objects.filter(
            order__customer_name__icontains=user.first_name,
            order__status='paid'
        ).aggregate(
            total=Sum(F('price_at_order') * F('quantity'), output_field=FloatField())
        )['total'] or 0

        return {
            'expenditure': expenditure,
            'paid orders': user_orders.filter(status="paid").count() or 0,
            'pending orders': user_orders.filter(status="pending").count() or 0,
            'cancelled orders': user_orders.filter(status="cancelled").count() or 0,
            'payments made': Payment.objects.filter(owner__icontains=user.username).count() or 0,
            'order count': user_orders.count() or 0,
        }
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from orders.models import OrderItem, Order
from payments.models import Payment
from products.models import Product
from django.db.models import Sum, F, FloatField
from django.contrib.auth import get_user_model
from django.utils.timezone import now, timedelta


class SalesStatsView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            total_orders_made = Order.objects
            customer_data : dict[str , int] = None
            admin_data : dict[str , int] = None

            if request.user.is_admin:            
                order_count = total_orders_made.count() or 0
                
                paid_orders = total_orders_made.filter(status="paid").count() or 0
                
                pending_orders = total_orders_made.filter(status="pending").count() or 0
                
                cancelled_orders = total_orders_made.filter(status="cancelled").count() or 0
                
                payments_made = Payment.objects.count() or 0
                
                past_week = now() - timedelta(days=7)
                revenue = (OrderItem.objects
                       .filter(order__created_at__gte=past_week)
                       .aggregate(total=Sum(F('price_at_order') * F('quantity'), output_field=FloatField()))
                      )
                      
                top_products = (OrderItem.objects
                            .values('product__id', 'product__name')
                            .annotate(total_sold=Sum('quantity'))
                            .order_by('-total_sold')[:5])
                            
                total_stock = Product.objects.aggregate(total=Sum('stock'))['total'] or 0
            
                User = get_user_model()
                customers = User.objects.filter(is_customer=True).count() or 0
                
                admin_data = {
                    'revenue(last 7 days)': revenue['total'] or 0,
                    'top products': list(top_products),
                    'total stock' : total_stock,
                    'customers' : customers,
                    'paid orders' : paid_orders,
                    'pending orders' : pending_orders,
                    'cancelled orders' : cancelled_orders,
                    'payments made': payments_made,
                    'order count' : order_count,
                }

                
                expenditure = (OrderItem.objects
                       .filter(order__customer_name__icontains=request.user.first_name)
                       .filter(order__status='paid')
                       .aggregate(total=Sum(F('price_at_order') * F('quantity'), output_field=FloatField()))
                      )
                
                user_orders = total_orders_made.filter(customer_name__icontains=request.user.first_name)
                paid_orders = user_orders.filter(status="paid").count() or 0
                
                pending_orders = user_orders.filter(status="pending").count() or 0
                
                cancelled_orders = user_orders.filter(status="cancelled").count() or 0
                
                payments_made = Payment.objects.filter(owner__icontains=request.user.username).count() or 0
                
                order_count = user_orders.count() or 0
            
                customer_data = {
                    'expenditure': expenditure['total'] or 0,
                    'paid orders' : paid_orders,
                    'pending orders' : pending_orders,
                    'cancelled orders' : cancelled_orders,
                    'payments made': payments_made,
                    'order count' : order_count,
                }

                return Response({'admin_data':admin_data,'customer_data':customer_data},status=status.HTTP_200_OK)
        else:
              return Response(status=status.HTTP_401_UNAUTHORIZED)



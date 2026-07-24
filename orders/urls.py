from django.urls import path
from .views import (
    AdminOrdersListAPIView,
    CustomerOrdersListAPIView,
    OrdersListCreateAPIView,
    OrdersRetrieveUpdateDestroyAPIView,
    CheckoutView
)

urlpatterns = [
    # Admin endpoint - all orders
    path('admin/', AdminOrdersListAPIView.as_view(), name='admin-orders-list'),
    
    # Customer endpoint - user's own orders
    path('my-orders/', CustomerOrdersListAPIView.as_view(), name='customer-orders-list'),
    
    # Detail endpoint
    path('<int:pk>', OrdersRetrieveUpdateDestroyAPIView.as_view(), name='order-detail'),
    
    # Checkout
    path('checkout', CheckoutView.as_view(), name='checkout'),
]

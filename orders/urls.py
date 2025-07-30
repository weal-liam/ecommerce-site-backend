from django.urls import path
from .views import *

Orders = OrdersViewSet.as_view(
    {
    'get': 'retrieve',
    'put': 'put',
    'patch': 'patch',
    'delete': 'delete'
    }
)

urlpatterns = [
    path('', OrdersViewSet.as_view({'get':'list','post':'post'}),name='order-list'),
    path('<int:pk>', Orders),
    path('checkout', CheckoutView.as_view(),name="checkout")
]

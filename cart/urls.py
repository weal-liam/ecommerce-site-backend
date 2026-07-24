from django.urls import path
from .views import CartViewSet

cart = CartViewSet.as_view({
    'get': 'cart_detail',
    'post': 'add_item',
    'delete': 'remove_item'
})

urlpatterns = [
    path('', cart, name='cart-list'),
    path('<int:pk>/', cart, name='cart-details'),
]

from django.urls import path
from .views import *

urlpatterns = [
    path('confirm', PaymentViewSet.as_view({'get': 'confirm_order'}), name='confirm_order'),
    path('',PaymentViewSet.as_view({'get':'list'}),name='payment-list')
]
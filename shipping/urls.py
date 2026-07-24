from django.urls import path

from .views import ShippingOptionListCreateAPIView

urlpatterns = [
    path('', ShippingOptionListCreateAPIView.as_view(), name='shipping-option-list'),
]
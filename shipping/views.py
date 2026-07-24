import logging

from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import ShippingOption
from .serializers import ShippingOptionSerializer

logger = logging.getLogger(__name__)


class ShippingOptionListCreateAPIView(generics.ListCreateAPIView):
    queryset = ShippingOption.objects.filter(is_active=True)
    serializer_class = ShippingOptionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset

import logging

from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Review
from .serializers import ReviewSerializer

logger = logging.getLogger(__name__)


class ReviewListCreateAPIView(generics.ListCreateAPIView):
    queryset = Review.objects.select_related('user', 'product').prefetch_related('replies__user').order_by('-reviewed_at')
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class ReviewDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.select_related('user', 'product').prefetch_related('replies__user').order_by('-reviewed_at')
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


ListCreateAPIView = ReviewListCreateAPIView
RetrieveUpdateDestoryAPIView = ReviewDetailAPIView


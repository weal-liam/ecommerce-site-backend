from django.urls import path

from .views import ReviewDetailAPIView, ReviewListCreateAPIView

urlpatterns = [
    path('', ReviewListCreateAPIView.as_view(), name='review-list'),
    path('<int:pk>/', ReviewDetailAPIView.as_view(), name='review-detail'),
]
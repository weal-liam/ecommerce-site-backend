from django.urls import path
from .views import ProductViewSet

product = ProductViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'destroy'
})

urlpatterns = [
    path('', ProductViewSet.as_view({'get': 'list','post': 'create','put':'update'}), name='product-list'),
    path('<int:pk>/', product, name='product-detail'),
]
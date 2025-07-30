from django.urls import path
from .views import CategoryViewSet

category = CategoryViewSet.as_view({
    'get': 'retrieve',
    'put': 'update',
    'delete': 'delete'
})

urlpatterns = [
    path('', CategoryViewSet.as_view({'get':'list','post': 'create'}),name='category-list'),
    path('<int:pk>/',category,name='category-detail')
]
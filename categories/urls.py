from django.urls import path
from . import views

urlpatterns = [
    path('', views.CategoryListCreateAPIView.as_view(), name='category-list'),
    path('<int:pk>/', views.CategoryRetrieveUpdateDestroyAPIView.as_view(), name='category-detail')
]
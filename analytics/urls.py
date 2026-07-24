from django.urls import path
from .views import AdminSalesStatsView, CustomerSalesStatsView

urlpatterns = [
    path('admin/', AdminSalesStatsView.as_view(), name='admin-sales-stats'),
    path('my-stats/', CustomerSalesStatsView.as_view(), name='customer-sales-stats'),
]

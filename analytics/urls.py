from django.urls import path
from .views import SalesStatsView

urlpatterns = [
    path('stats/', SalesStatsView.as_view(), name='sales-stats'),
]

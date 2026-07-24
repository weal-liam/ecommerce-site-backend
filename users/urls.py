from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import UserView, CustomTokenView, RegisterView

User = UserView.as_view(
    {
        'get': 'retrieve',
        'put': 'put'
    }
)
Register = RegisterView.as_view({
    'post': 'post'
})

urlpatterns = [
    path('login/', CustomTokenView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', Register, name='user-register'),
    path('', UserView.as_view({'get': 'list'}), name='user-list'),
    path('me/', User, name='user-me'),
    path('<int:pk>/', User, name='user-detail'),
]
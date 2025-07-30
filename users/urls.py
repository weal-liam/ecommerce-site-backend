from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import UserView, CustomTokenView, RegisterView

User = UserView.as_view(
    {
        'get' : 'retrieve',
        'put' : 'put'
    }
)
Register = RegisterView.as_view({
    'post' : 'post'
})

urlpatterns = [
    path('session/', CustomTokenView.as_view(),name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(),name='token_refresh'),
    path('login/',Register,name='user'),
    path('',UserView.as_view({'get':'list'}),name='user-list'),
    path('user',User,name='user-detail'),
    path('user/<int:pk>',User,name='user-detail'),
]
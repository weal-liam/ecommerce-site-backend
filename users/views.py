import logging
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import User
from users.serializers import UserSerializer, CustomTokenObtainPairSerializer

logger = logging.getLogger(__name__)


class CustomTokenView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code != status.HTTP_200_OK:
            return response

        data = response.data
        access_token = data.get('access')
        refresh_token = data.get('refresh')

        if access_token:
            response.set_cookie(
                'access_token',
                access_token,
                httponly=True,
                secure=getattr(settings, 'SESSION_COOKIE_SECURE', True),
                samesite='Lax',
                max_age=60 * 60 * 24,
            )

        if refresh_token:
            response.set_cookie(
                'refresh_token',
                refresh_token,
                httponly=True,
                secure=getattr(settings, 'SESSION_COOKIE_SECURE', True),
                samesite='Lax',
                max_age=60 * 60 * 24 * 7,
            )

        response.data = {
            'message': 'Login successful',
            'user': UserSerializer(request.user).data if request.user.is_authenticated else None,
        }
        return response

class RegisterView(viewsets.ViewSet):
    permission_classes = [AllowAny]
    def post(self, request):
        fullname = request.data.get('fullname', '').strip()
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')

        if not first_name and fullname:
            parts = fullname.split()
            first_name = parts[0]
            last_name = ' '.join(parts[1:]) if len(parts) > 1 else ''

        username = request.data.get('username') or request.data.get('email')
        email = request.data.get('email')
        password = request.data.get('password')

<<<<<<< HEAD
        if not email or not password:
            return Response({'error': 'email and password are required'}, status=status.HTTP_400_BAD_REQUEST)
        # Normalize username fallback
        if not username:
            username = email.split('@')[0]

        # Check for existing users by email and username
        existing_by_email = User.objects.filter(email=email).first()
        existing_by_username = User.objects.filter(username=username).first() if username else None

        # If either attribute already exists, decide whether this is a login attempt
        if existing_by_email or existing_by_username:
            # If both point to different users -> conflict
            if existing_by_email and existing_by_username and existing_by_email.pk != existing_by_username.pk:
                return Response({'error': 'Email and username are already taken by different accounts'}, status=status.HTTP_400_BAD_REQUEST)

            # Pick the existing user (either one will do if they are the same)
            user = existing_by_email or existing_by_username

            # If password matches, treat as login and return the user
            if user.check_password(password):
                serializer = UserSerializer(user)
                return Response({'message': 'Login successful', 'user': serializer.data}, status=status.HTTP_200_OK)

            # Otherwise, refuse registration because the provided attributes are already in use
            conflicts = []
            if existing_by_email:
                conflicts.append('email')
            if existing_by_username:
                conflicts.append('username')
            return Response({'error': f"{', '.join(conflicts)} already in use"}, status=status.HTTP_400_BAD_REQUEST)
        data = {
            'first_name': first_name or '',
            'last_name': last_name or '',
            'username': username,
            'email': email,
            'password': password,
=======
        data ={
            'first_name' : first_name,
            'last_name' : second_name,
            'username' : user_name,
            'email' : email,
            'password' : password,
            'is_superuser': False if not users == 0 else True
>>>>>>> parent of 15deffb (new age)
        }

        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            is_first_user = not User.objects.exists()
            user = serializer.save()
            if is_first_user:
                user.is_admin = True
                user.is_staff = True
                user.is_superuser = True
                user.is_customer = False
                user.is_vendor = False
                user.save()
            return Response({'message': 'User created', 'user': serializer.data}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def retrieve(self, request, pk=None):
        if pk is not None and pk != request.user.pk and not getattr(request.user, 'is_admin', False):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        user = get_object_or_404(User, pk=pk) if pk is not None else request.user
        serializer = UserSerializer(user)
        return Response({'user': serializer.data}, status=status.HTTP_200_OK)

    def list(self, request):
        if not getattr(request.user, 'is_admin', False):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk=None):
        if pk is not None and pk != request.user.pk and not getattr(request.user, 'is_admin', False):
            return Response({'detail': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)

        user = get_object_or_404(User, pk=pk) if pk is not None else request.user
        serializer = UserSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


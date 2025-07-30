import json
from typing import Any

from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework_simplejwt.views import TokenObtainPairView

from users.models import User
from users.serializers import UserSerializer, CustomTokenObtainPairSerializer


# Create your views here.
class CustomTokenView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class RegisterView(viewsets.ViewSet):
    def post(self,request):
        names = request.data.get('fullname',' ').split()
        first_name  = names[0] if len(names) > 0 else ''
        second_name = names[1] if len(names) > 1 else ''
        user_name = request.data.get('username') or first_name
        email = request.data.get('email')
        password = request.data.get('password')
        
        users = User.objects.count()

        data ={
            'first_name' : first_name,
            'last_name' : second_name,
            'username' : user_name,
            'email' : email,
            'password' : password,
            'is_superuser': False if not users == 0 else True
        }
        user = authenticate(
            request,
            username=user_name,
            email=email,
            password=password
            )
        if user:
            serializer = UserSerializer(user)
            return Response({'user':serializer.data},status=status.HTTP_200_OK)
            
        serializer = UserSerializer(data=data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({'message':'User created','user':serializer.data},status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)

class UserView(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]
    def retrieve(self,request,pk=None):
        if pk:
            user = User.objects.get(pk=pk)
            serializer = UserSerializer(user)
        elif request.user:
            user = request.user
            serializer = UserSerializer(user)
            
        return Response({'user':serializer.data},status=status.HTTP_200_OK) if serializer else (
                Response(status=status.HTTP_400_BAD_REQUEST))
            
            
    def list(self,request):   
            query = User.objects.all()
            serializer = UserSerializer(query,many=True)
        
            return Response(serializer.data,status=status.HTTP_200_OK) if serializer else (
                Response(status=status.HTTP_400_BAD_REQUEST))
    

    def put(self,request,pk=None):
        user = request.user
        if pk:
            try:
                user = User.objects.get(pk=pk)
            except User.DoesNotExist:
                return Response({'error': 'user not found'}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


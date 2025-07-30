from typing import Any

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import Token

from users.models import User

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: User) -> Token:
        token = super().get_token(user)
        token['username'] = user.username
        return token

    def validate(self, attrs: dict[str, Any]) -> dict[str, str]:
        attrs['username'] = attrs.get('username')
        return super().validate(attrs)

class UserSerializer(serializers.ModelSerializer):
    date_joined = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {'password' : {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

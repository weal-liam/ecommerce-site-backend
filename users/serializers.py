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
<<<<<<< HEAD
    date_joined = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)
    password = serializers.CharField(write_only=True, required=True)
    profile_image = serializers.ImageField(required=False, allow_null=True)
    profile_image_url = serializers.URLField(required=False, allow_null=True)
=======
    date_joined = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
>>>>>>> parent of 15deffb (new age)

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'username',
            'email',
            'password',
            'profile_image',
            'profile_image_url',
            'is_customer',
            'is_vendor',
            'is_admin',
            'date_joined',
        )
        read_only_fields = ('is_admin', 'date_joined')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

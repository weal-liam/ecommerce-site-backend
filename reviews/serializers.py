from rest_framework import serializers

from products.models import Product
from users.models import User

from .models import Reply, Review


class ReviewerSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile_image']

    def get_profile_image(self, obj):
        if obj.profile_image:
            return obj.profile_image.url if hasattr(obj.profile_image, 'url') else obj.profile_image
        return obj.profile_image_url


class ReplySerializer(serializers.ModelSerializer):
    user = ReviewerSerializer(read_only=True)
    replied_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)

    class Meta:
        model = Reply
        fields = ['id', 'user', 'message', 'replied_at', 'likes', 'dislikes']


class ReviewSerializer(serializers.ModelSerializer):
    user = ReviewerSerializer(read_only=True)
    replies = ReplySerializer(many=True, read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),
        source='product',
        write_only=True,
    )
    reviewed_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)

    class Meta:
        model = Review
        fields = [
            'id',
            'user',
            'product',
            'product_id',
            'comment',
            'rating',
            'reviewed_at',
            'likes',
            'dislikes',
            'replies',
        ]
        read_only_fields = ['id', 'user', 'product', 'reviewed_at', 'likes', 'dislikes', 'replies']

    def create(self, validated_data):
        request = self.context.get('request')
        if request is None or not getattr(request.user, 'is_authenticated', False):
            raise serializers.ValidationError({'detail': 'Authentication required to create a review.'})

        validated_data['user'] = request.user
        return Review.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
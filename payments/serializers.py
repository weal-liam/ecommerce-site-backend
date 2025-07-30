from rest_framework import serializers

from payments.models import Payment
from users.serializers import UserSerializer


class PaymentSerializer(serializers.ModelSerializer):
    paid_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = Payment
        fields = '__all__'
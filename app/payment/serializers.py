from rest_framework import serializers

from app.payment.models import (
    PaymentMethod,
    PaymentTransaction,
    PaymentMethodType,
)


class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__'


class PaymentTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentTransaction
        fields = '__all__'


########################
# Booking Payment
########################
class PurchaseBookingSerializer(serializers.Serializer):
    payment_method_type = serializers.ChoiceField(choices=PaymentMethodType.choices, required=True)
    payment_details = serializers.JSONField(required=True)

    def validate(self, attrs):
        validated_data = super().validate(attrs)

        payment_method_type = validated_data.get('payment_method_type')
        if not payment_method_type:
            raise serializers.ValidationError('Payment method type is required')

        payment_details = validated_data.get('payment_details')
        if not payment_details:
            raise serializers.ValidationError('Payment details is required')

        return validated_data
    
    def validate_payment_method_type(self, value):
        is_exist = PaymentMethod.objects.filter(
            type=value,
            is_enabled=True,
        ).exists()
        if not is_exist:
            raise serializers.ValidationError('Payment method not found')

        return value

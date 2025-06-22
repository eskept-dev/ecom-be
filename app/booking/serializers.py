from rest_framework import serializers
from django.db import transaction

from app.booking.models import (
    Booking, BookingItem,
    CONTACT_INFO_REQUIRED_FIELDS,
    GUEST_INFO_REQUIRED_FIELDS,
    PaymentMethod,
)

from app.product.models import Product


########################
# Booking
########################
class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
        extra_kwargs = {
            'customer': {'read_only': True},
            'code': {'read_only': True},
            'currency': {'required': True},
            'is_self_booking': {'required': True},
            'contact_info': {'required': True},
            'guest_info': {'required': True},
            'details': {'required': True},
        }
        
    def validate(self, attrs):
        validated_data = super().validate(attrs)

        is_self_booking = validated_data.get('is_self_booking', True)

        if not Booking.validate_booking_detail_section(validated_data.get('contact_info'), CONTACT_INFO_REQUIRED_FIELDS):
            raise serializers.ValidationError({'contact_info': 'Invalid contact info'})

        if not is_self_booking and not Booking.validate_booking_detail_section(validated_data.get('guest_info'), GUEST_INFO_REQUIRED_FIELDS):
            raise serializers.ValidationError({'guest_info': 'Invalid guest info'})
        
        if is_self_booking:
            validated_data['guest_info'] = validated_data.get('contact_info')

        return validated_data

    def create(self, validated_data):
        validated_data['customer'] = self.context['request'].user
        return super().create(validated_data)
        
        
class AddBookingItemSerializer(serializers.ModelSerializer):
    product_code_name = serializers.CharField(required=True)

    class Meta:
        model = BookingItem
        fields = '__all__'
        extra_kwargs = {
            'booking': {'read_only': True},
            'product': {'read_only': True},
            'total': {'read_only': True},
        }
        
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError('Quantity must be greater than 0')
        return value
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError('Price must be greater than 0')
        return value
    
    def validate(self, attrs):
        validated_data = super().validate(attrs)
        
        booking = self.context.get('booking')
        if not booking:
            raise serializers.ValidationError('Booking is required')
        validated_data['booking'] = booking
        
        product = Product.objects.get(code_name=validated_data.get('product_code_name'))
        if not product:
            raise serializers.ValidationError('Product not found')
        validated_data['product'] = product

        return validated_data
    
    def create(self, validated_data):
        validated_data.pop('product_code_name')
        booking_item = BookingItem.objects.create(**validated_data)
        return booking_item


class AddBookingItemsPayloadSerializer(serializers.Serializer):
    items = AddBookingItemSerializer(many=True)

    def create(self, validated_data):
        booking = self.context.get('booking')
        if not booking:
            raise serializers.ValidationError('Booking is required')

        items = validated_data.get('items', [])
        if not items:
            raise serializers.ValidationError({'items': 'At least one item is required'})

        with transaction.atomic():
            BookingItem.objects.filter(booking=booking).delete()

            for index, item in enumerate(items):
                item['index'] = index + 1
                serializer = AddBookingItemSerializer(data=item, context={'booking': booking})
                serializer.is_valid(raise_exception=True)
                serializer.save()

            booking.refresh_from_db()

        return booking


class DeleteBookingItemsPayloadSerializer(serializers.Serializer):
    booking_item_ids = serializers.ListField(child=serializers.IntegerField(), required=True)

    def validate(self, attrs):
        validated_data = super().validate(attrs)
        return validated_data

    def create(self, validated_data):
        booking = self.context.get('booking')
        if not booking:
            raise serializers.ValidationError('Booking is required')
        
        booking_item_ids = validated_data.get('booking_item_ids', [])
        if not booking_item_ids:
            raise serializers.ValidationError({'booking_item_ids': 'At least one item is required'})
        
        booking_items = BookingItem.objects.filter(id__in=booking_item_ids, booking=booking)
        if not booking_items.exists() and len(booking_item_ids) != booking_items.count():
            raise serializers.ValidationError({'booking_item_ids': 'Booking items not found'})

        booking_items.delete()

        return booking


########################
# Booking Item
########################
class BookingItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingItem
        fields = '__all__'
        extra_kwargs = {
            'booking': {'read_only': True},
            'product': {'read_only': True},
            'total': {'read_only': True},
            'index': {'read_only': True},
        }


########################
# Payment Method
########################
class PaymentMethodSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentMethod
        fields = '__all__'

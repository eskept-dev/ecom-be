from rest_framework import serializers
from django.db import transaction

from app.booking.models import (
    Booking, BookingEventHistory, BookingItem,
    CONTACT_INFO_REQUIRED_FIELDS,
    GUEST_INFO_REQUIRED_FIELDS,
)

from app.payment.models import (
    PaymentMethod,
    PaymentMethodType,
)
from app.product.models import Product
from app.product.serializers import ProductSerializer


########################
# Booking
########################
class BookingSerializer(serializers.ModelSerializer):
    service_types = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = '__all__'
        extra_kwargs = {
            'customer': {'read_only': True, 'required': False},
            'code': {'read_only': True},
            'currency': {'required': True},
            'is_self_booking': {'required': True},
            'contact_info': {'required': True},
            'guest_info': {'required': True},
            'details': {'required': True},
            'service_types': {'read_only': True},
        }
        
    def get_service_types(self, obj):
        return obj.bookingitem_set.values_list('product__service_type', flat=True)
        
    def validate(self, attrs):
        validated_data = super().validate(attrs)

        is_self_booking = validated_data.get('is_self_booking', True)
        is_confirmed_to_cancellation_policy = validated_data.get('is_confirmed_to_cancellation_policy', False)

        if not Booking.validate_booking_detail_section(validated_data.get('contact_info'), CONTACT_INFO_REQUIRED_FIELDS):
            raise serializers.ValidationError({'contact_info': 'Invalid contact info'})

        if not is_self_booking and not Booking.validate_booking_detail_section(validated_data.get('guest_info'), GUEST_INFO_REQUIRED_FIELDS):
            raise serializers.ValidationError({'guest_info': 'Invalid guest info'})
        
        if is_self_booking:
            validated_data['guest_info'] = validated_data.get('contact_info')
            
        if not is_confirmed_to_cancellation_policy:
            raise serializers.ValidationError({'is_confirmed_to_cancellation_policy': 'You must confirm to the cancellation policy'})

        if self.context['request'].user.is_authenticated:
            validated_data['customer'] = self.context['request'].user
        else:
            validated_data['customer'] = None

        return validated_data


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
class BookingItemProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'code_name', 'name', 'image_url', 'price_vnd', 'price_usd']


class BookingItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    
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
# Booking Event History
########################
class BookingEventHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingEventHistory
        fields = ('created_at', 'event_type', 'instance_type', 'instance_id', 'description')

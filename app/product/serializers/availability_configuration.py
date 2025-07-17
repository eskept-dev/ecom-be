from rest_framework import serializers

from app.product.models import ProductAvailabilityConfiguration, Product


class ProductAvailabilityConfigurationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAvailabilityConfiguration
        fields = "__all__"
        extra_kwargs = {
            "code": {"read_only": True},
        }
        
    def validate(self, attrs):
        self.validate_duplicated(attrs)
        
        return super().validate(attrs)
    
    def validate_duplicated(self, attrs):
        if ProductAvailabilityConfiguration.objects.filter(
            products__in=attrs['products'],
            type=attrs['type'],
            start_date__lte=attrs['end_date'],
            end_date__gte=attrs['start_date'],
            is_deleted=False,
        ).exists():
            raise serializers.ValidationError("Duplicated availability configuration")

    def create(self, *args, **kwargs):
        try:
            return super().create(*args, **kwargs)
        except Exception as e:
            raise serializers.ValidationError(e)

    def update(self, *args, **kwargs):
        try:
            return super().update(*args, **kwargs)
        except Exception as e:
            raise serializers.ValidationError(e)


class GetAvailabilityCalendarRequestSerializer(serializers.Serializer):
    product_ids = serializers.ListField(child=serializers.IntegerField(), required=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)
    
    
class CalendarProductAvailabilityConfigurationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductAvailabilityConfiguration
        fields = ('id', 'code', 'name', 'type', 'value')


class CalendarProductItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'service_type')


class ProductAvailabilityItemDetailSerializer(serializers.Serializer):
    product = CalendarProductItemSerializer(required=True)
    availability_configuration = CalendarProductAvailabilityConfigurationItemSerializer(required=True)
    max_capacity = serializers.IntegerField(required=True)
    
class ProductAvailabilityItemSerializer(serializers.Serializer):
    date = serializers.DateField(required=True)
    availabilities = serializers.ListField(child=ProductAvailabilityItemDetailSerializer(), required=True)


class BlockProductAvailabilityRequestSerializer(serializers.Serializer):
    product_ids = serializers.ListField(child=serializers.IntegerField(), required=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)


class UnblockProductAvailabilityRequestSerializer(serializers.Serializer):
    product_ids = serializers.ListField(child=serializers.IntegerField(), required=True)
    start_date = serializers.DateField(required=True)
    end_date = serializers.DateField(required=True)

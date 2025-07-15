from rest_framework import serializers

from app.product.models import ProductPriceConfiguration


class ProductPriceConfigurationSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductPriceConfiguration
        fields = '__all__'
        extra_kwargs = {
            'code': {'read_only': True},
        }

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


class ProductPricePreviewRequestSerializer(serializers.Serializer):
    product_ids = serializers.ListField(child=serializers.IntegerField(), required=True)


class ProductPricePreviewResponseSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    price_configuration_id = serializers.IntegerField()
    price_configuration_name = serializers.CharField()
    base_price_vnd = serializers.DecimalField(max_digits=10, decimal_places=2)
    price_vnd = serializers.DecimalField(max_digits=10, decimal_places=2)
    base_price_usd = serializers.DecimalField(max_digits=10, decimal_places=2)
    price_usd = serializers.DecimalField(max_digits=10, decimal_places=2)

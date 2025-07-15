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
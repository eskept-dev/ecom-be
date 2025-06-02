from rest_framework import serializers

from app.product.models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'code_name': {'read_only': True},
        }

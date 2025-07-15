from rest_framework import serializers

from app.product.models import Product


class ProductSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source="supplier.name", read_only=True)

    class Meta:
        model = Product
        fields = "__all__"
        extra_kwargs = {
            "code_name": {"read_only": True},
            "rating": {"read_only": True},
            "review_count": {"read_only": True},
        }

    def validate(self, attrs):
        attrs = super().validate(attrs)

        what_nexts = attrs.get("what_nexts")
        if not what_nexts:
            attrs["what_nexts"] = []

        highlights = attrs.get("highlights")
        if not highlights:
            attrs["highlights"] = []

        return attrs


class ProductWithPriceConfigurationSerializer(ProductSerializer):
    price_configuration_id = serializers.IntegerField(read_only=True)
    price_configuration_name = serializers.CharField(read_only=True)
    price_vnd = serializers.FloatField(read_only=True)
    price_usd = serializers.FloatField(read_only=True)

    class Meta(ProductSerializer.Meta):
        model = Product
        fields = '__all__'

    def to_representation(self, instance):
        data = super().to_representation(instance)

        applied_price = self.context.get("applied_price")
        if applied_price:
            return self.to_representation_for_single_product(instance)
        
        applied_prices = self.context.get("applied_prices")
        if applied_prices:
            return self.to_representation_for_multiple_products(instance)

        return data
    
    def to_representation_for_single_product(self, instance):
        data = super().to_representation(instance)

        applied_price = self.context.get("applied_price", {})

        data['price_configuration_id'] = applied_price.price_configuration_id
        data['price_configuration_name'] = applied_price.price_configuration_name
        data['base_price_vnd'] = float(applied_price.base_price_vnd)
        data['price_vnd'] = float(applied_price.price_vnd)
        data['base_price_usd'] = float(applied_price.base_price_usd)
        data['price_usd'] = float(applied_price.price_usd)

        return data
    
    def to_representation_for_multiple_products(self, instance):
        data = super().to_representation(instance)

        applied_prices = self.context.get("applied_prices", {})
        applied_price = applied_prices.get(str(instance.id), {})

        data['price_configuration_id'] = applied_price.price_configuration_id
        data['price_configuration_name'] = applied_price.price_configuration_name
        data['base_price_vnd'] = float(applied_price.base_price_vnd)
        data['price_vnd'] = float(applied_price.price_vnd)
        data['base_price_usd'] = float(applied_price.base_price_usd)
        data['price_usd'] = float(applied_price.price_usd)

        return data

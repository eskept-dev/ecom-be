from rest_framework import serializers

from app.product.models import Product


class ProductSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)

    class Meta:
        model = Product
        fields = '__all__'
        extra_kwargs = {
            'code_name': {'read_only': True},
            'rating': {'read_only': True},
            'review_count': {'read_only': True},
        }

    def validate(self, attrs):
        attrs = super().validate(attrs)

        what_nexts = attrs.get('what_nexts')
        if not what_nexts:
            attrs['what_nexts'] = []

        highlights = attrs.get('highlights')
        if not highlights:
            attrs['highlights'] = []

        return attrs

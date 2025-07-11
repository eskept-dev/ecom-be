from rest_framework import serializers

from app.product.models import Product
from app.supplier.models import Supplier


class SupplierSerializer(serializers.ModelSerializer):
    services = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Supplier
        fields = '__all__'

    def get_services(self, obj):
        return list(
            Product.objects.filter(supplier=obj).distinct('service_type').values_list('service_type', flat=True)
        )

import django_filters
from django.db.models import Q

from app.supplier.models import Supplier
from app.product.models import Product


class SupplierFilter(django_filters.FilterSet):
    service = django_filters.CharFilter(method='filter_by_service')
    status = django_filters.CharFilter(method='filter_by_status')
    
    class Meta:
        model = Supplier
        fields = ['service', 'status']
        
    def filter_by_service(self, queryset, name, value):
        products = Product.objects.filter(service=value)
        supplier_ids = products.values_list('supplier', flat=True)
        return queryset.filter(id__in=supplier_ids)

    def filter_by_status(self, queryset, name, value):
        return queryset.filter(status=value)

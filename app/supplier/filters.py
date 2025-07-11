import django_filters

from app.supplier.models import Supplier


class SupplierFilter(django_filters.FilterSet):
    services = django_filters.CharFilter(method='filter_by_services')
    statuses = django_filters.CharFilter(method='filter_by_statuses')

    class Meta:
        model = Supplier
        fields = ['services', 'statuses']

    def filter_by_services(self, queryset, name, value):
        services_to_filter = value.split(',')
        return queryset.filter(products__service_type__in=services_to_filter)

    def filter_by_statuses(self, queryset, name, value):
        statuses_to_filter = value.split(',')
        return queryset.filter(status__in=statuses_to_filter)

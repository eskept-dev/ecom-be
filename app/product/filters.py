import django_filters
from django.db.models import Q

from app.product.models import Product, ServiceType, Currency


class ProductFilter(django_filters.FilterSet):
    # Shared
    service = django_filters.CharFilter(method='filter_by_service')
    rating = django_filters.NumberFilter(field_name='rating', lookup_expr='gte')
    price_min = django_filters.NumberFilter(method='filter_by_price_min')
    price_max = django_filters.NumberFilter(method='filter_by_price_max')
    currency = django_filters.CharFilter(method='filter_by_currency')
    suppliers = django_filters.CharFilter(method='filter_by_suppliers')
    province = django_filters.CharFilter(method='filter_by_province')
    city = django_filters.CharFilter(method='filter_by_city')
    district = django_filters.CharFilter(method='filter_by_district')
    ward = django_filters.CharFilter(method='filter_by_ward')
    
    # Airport service
    number_of_travellers = django_filters.NumberFilter(method='filter_by_number_of_travellers')
    number_of_days = django_filters.NumberFilter(method='filter_by_number_of_days')
    
    # Fast track
    available_time_from = django_filters.DateTimeFilter(method='filter_by_available_time_from')
    available_time_to = django_filters.DateTimeFilter(method='filter_by_available_time_to')
    
    # E-visa
    processing_time = django_filters.NumberFilter(method='filter_by_processing_time')

    class Meta:
        model = Product
        fields = [
            'service', 'rating', 'price_min', 'price_max',
            'suppliers', 'currency', 'province', 'city', 'district', 'ward',
        ]

    def filter_by_suppliers(self, queryset, name, value):
        supplier_names = value.split(',')
        return queryset.filter(supplier__id__in=supplier_names)

    def filter_by_province(self, queryset, name, value):
        return queryset.filter(available_locations__contains=[{'province': value}])
    
    def filter_by_city(self, queryset, name, value):
        return queryset.filter(available_locations__contains=[{'city': value}])
    
    def filter_by_district(self, queryset, name, value):
        return queryset.filter(available_locations__contains=[{'district': value}])
    
    def filter_by_ward(self, queryset, name, value):
        return queryset.filter(available_locations__contains=[{'ward': value}])

    def filter_by_service(self, queryset, name, value):
        if value == ServiceType.AIRPORT_TRANSFER.value:
            service_value_to_filter = ServiceType.AIRPORT_TRANSFER
        elif value == ServiceType.FAST_TRACK.value:
            service_value_to_filter = ServiceType.FAST_TRACK
        elif value == ServiceType.E_VISA.value:
            service_value_to_filter = ServiceType.E_VISA
        else:
            return queryset
        
        return queryset.filter(service_type=service_value_to_filter)
    
    def filter_by_currency(self, queryset, name, value):
        return queryset

    def filter_by_price_min(self, queryset, name, value):
        currency_selected = self.form.cleaned_data.get('currency')
        
        if currency_selected == Currency.VND.value:
            return queryset.filter(price_vnd__gte=value)
        return queryset.filter(price_usd__gte=value)

    def filter_by_price_max(self, queryset, name, value):
        currency_selected = self.form.cleaned_data.get('currency')
        
        if currency_selected == Currency.VND.value:
            return queryset.filter(price_vnd__lte=value)
        return queryset.filter(price_usd__lte=value)

    # # Airport service
    # def filter_by_number_of_travellers(self, queryset, name, value):
    #     return queryset.filter(details__contains=[{'number_of_travellers': value}])
    
    # def filter_by_number_of_days(self, queryset, name, value):
    #     return queryset.filter(details__contains=[{'number_of_days': value}])
    
    # # Fast track
    # def filter_by_available_time_from(self, queryset, name, value):
    #     return queryset.filter(details__available_time_from=value)
    
    # def filter_by_available_time_to(self, queryset, name, value):
    #     return queryset.filter(details__available_time_to=value)

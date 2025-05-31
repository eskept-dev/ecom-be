from django.db.models import Q, Case, When, Value, IntegerField
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from app.base.pagination import CustomPagination
from app.core.utils.string import slugify
from app.location import serializers
from app.location.models import Location


DEFAULT_CACHE_TIME = 60 * 60 * 24
LARGE_NUMBER = 999999


class LocationModelViewSet(ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = serializers.LocationSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        search_query = self.request.query_params.get('search', None)
        location_type = self.request.query_params.get('type', None)
        province = self.request.query_params.get('province', None)
        city = self.request.query_params.get('city', None)
        district = self.request.query_params.get('district', None)
        ward = self.request.query_params.get('ward', None)
        
        queryset = super().get_queryset()
        queryset = queryset.filter(is_enabled=True)

        queryset = queryset.annotate(
            custom_order=Case(
                When(order=0, then=Value(LARGE_NUMBER)),
                default='order',
                output_field=IntegerField(),
            )
        ).order_by('custom_order', 'name')

        if location_type:
            queryset = queryset.filter(type=location_type)

        if province:
            queryset = queryset.filter(province=slugify(province))

        if city:
            queryset = queryset.filter(city=slugify(city))

        if district:
            queryset = queryset.filter(district=slugify(district))

        if ward:
            queryset = queryset.filter(ward=slugify(ward))

        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) |
                Q(code__icontains=search_query) |
                Q(address__icontains=search_query) |
                Q(province__icontains=search_query) |
                Q(city__icontains=search_query) |
                Q(district__icontains=search_query) |
                Q(ward__icontains=search_query)
            )

        return queryset

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'retrieve']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        _list_action = lambda req, *a, **k: super(LocationModelViewSet, self).list(req, *a, **k)

        if request.query_params.get('search', None):
            return _list_action(request, *args, **kwargs)
        else:
            cached_list_view = cache_page(DEFAULT_CACHE_TIME)(_list_action)
            return cached_list_view(request, *args, **kwargs)

    @method_decorator(cache_page(DEFAULT_CACHE_TIME))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

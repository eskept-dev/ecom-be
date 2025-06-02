from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from app.base.pagination import CustomPagination
from app.product import serializers
from app.product.filters import ProductFilter
from app.product.models import Product


DEFAULT_CACHE_TIME = 60 * 60 * 24


class ProductModelViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = serializers.ProductSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "code_name", "supplier__name"]
    ordering_fields = ["price_vnd", "price_usd", "rating", "review_count"]

    def get_filter_backends(self):
        if self.action == "retrieve":
            return []
        return super().get_filter_backends()

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def list(self, request, *args, **kwargs):
        _list_action = lambda req, *a, **k: super(ProductModelViewSet, self).list(
            req, *a, **k
        )

        if request.query_params.get("search", None):
            return _list_action(request, *args, **kwargs)
        else:
            cached_list_view = cache_page(DEFAULT_CACHE_TIME)(_list_action)
            return cached_list_view(request, *args, **kwargs)

    @method_decorator(cache_page(DEFAULT_CACHE_TIME))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

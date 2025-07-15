from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from app.core.utils.logger import logger
from app.base.pagination import CustomPagination
from app.base.mixins import SoftDeleteViewSetMixin

from app.product import serializers
from app.product.filters import ProductFilter
from app.product.models import Product, ProductUnit
from app.product.services import products as products_service


class ProductModelViewSet(SoftDeleteViewSetMixin, ModelViewSet):    
    queryset = Product.objects.filter(is_deleted=False)
    serializer_class = serializers.ProductSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["id", "name", "code_name", "supplier__name"]
    ordering_fields = [
        "base_price_vnd",
        "base_price_usd",
        "rating",
        "review_count",
        "name",
        "created_at",
        "id",
        "status",
        "supplier",
    ]
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @method_decorator(cache_page(60 * 60 * 24, key_prefix="product_list"))
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        paginator = CustomPagination()
        page = paginator.paginate_queryset(queryset, request)

        products = page if page is not None else queryset
        product_ids = [product.id for product in products]

        applied_prices = products_service.apply_price_configuration_to_products(product_ids)

        serializer = serializers.ProductWithPriceConfigurationSerializer(
            products,
            many=True,
            context={"applied_prices": applied_prices},
        )

        if page is not None:
            return paginator.get_paginated_response(serializer.data)

        return Response(serializer.data)
    
    @method_decorator(cache_page(60 * 60 * 24, key_prefix="product_retrieve"))
    def retrieve(self, request, *args, **kwargs):
        product = self.get_object()
        applied_product_price = products_service.get_applied_product_price(product.id)
        
        serializer = serializers.ProductWithPriceConfigurationSerializer(
            product,
            context={"applied_price": applied_product_price},
        )
        
        return Response(serializer.data)

    def _clear_cache(self):
        keys = cache.keys(f"*product*")
        cache.delete_many(keys)

    def create(self, request, *args, **kwargs):
        self._clear_cache()
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        self._clear_cache()
        return super().update(request, *args, **kwargs)
        
    def destroy(self, request, *args, **kwargs):
        self._clear_cache()
        return super().destroy(request, *args, **kwargs)
    
    def partial_update(self, request, *args, **kwargs):
        self._clear_cache()
        return super().partial_update(request, *args, **kwargs)


class ProductUnitAPIView(APIView):
    permission_classes = [AllowAny]

    @method_decorator(cache_page(60 * 60 * 24))
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get(self, request):
        response = [
            {'value': unit[0], 'label': unit[1]}
            for unit in ProductUnit.choices
        ]
        
        return Response({
            'data': response
        })

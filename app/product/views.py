from django_filters.rest_framework import DjangoFilterBackend
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from app.base.pagination import CustomPagination
from app.base.mixins import (
    SoftDeleteViewSetMixin,
)
from app.product import serializers
from app.product.filters import ProductFilter
from app.product.models import Product, ProductUnit


class ProductModelViewSet(ModelViewSet, SoftDeleteViewSetMixin):    
    queryset = Product.objects.filter(is_deleted=False)
    serializer_class = serializers.ProductSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["id", "name", "code_name", "supplier__name"]
    ordering_fields = [
        "price_vnd",
        "price_usd",
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
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(60 * 60 * 24, key_prefix="product_retrieve"))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

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

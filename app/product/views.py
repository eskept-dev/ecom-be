from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from app.base.pagination import CustomPagination
from app.base.mixins import (
    SoftDeleteViewSetMixin,
    ListCacheViewSetMixin,
    RetrieveCacheViewSetMixin,
)
from app.product import serializers
from app.product.filters import ProductFilter
from app.product.models import Product


class ProductModelViewSet(ModelViewSet,
                        SoftDeleteViewSetMixin,
                        ListCacheViewSetMixin,
                        RetrieveCacheViewSetMixin):
    queryset = Product.objects.filter(is_deleted=False)
    serializer_class = serializers.ProductSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ["name", "code_name", "supplier__name"]
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

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

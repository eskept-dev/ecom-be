from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.viewsets import ModelViewSet

from app.auth.permissions import IsInternalUser
from app.base.pagination import CustomPagination
from app.base.mixins import SoftDeleteViewSetMixin
from app.product import serializers
from app.product.models import ProductPriceConfiguration


class ProductPriceConfigurationModelViewSet(SoftDeleteViewSetMixin, ModelViewSet):
    queryset = ProductPriceConfiguration.objects.filter(is_deleted=False)
    serializer_class = serializers.ProductPriceConfigurationSerializer
    permission_classes = [IsInternalUser]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['code', 'name']
    ordering_fields = [
        'created_at', 'code', 'name', 'is_active', 'adjustment_type', 'time_range_type']
    ordering = ['-created_at']

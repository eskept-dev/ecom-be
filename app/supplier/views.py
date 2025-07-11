from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache

from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from app.base.pagination import CustomPagination
from app.base.mixins import SoftDeleteViewSetMixin
from app.core.utils.logger import logger
from app.supplier import serializers
from app.supplier.filters import SupplierFilter
from app.supplier.models import Supplier


class SupplierModelViewSet(ModelViewSet, SoftDeleteViewSetMixin):
    queryset = Supplier.objects.filter(is_deleted=False)
    serializer_class = serializers.SupplierSerializer
    pagination_class = CustomPagination
    filter_backends = [SearchFilter, OrderingFilter]
    filterset_class = SupplierFilter
    search_fields = ['name', 'contact_phone_number', 'contact_email']
    ordering_fields = ['created_at', 'updated_at', 'name', 'id']
    ordering = ['-created_at']

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @method_decorator(cache_page(60 * 60 * 24, key_prefix="supplier_list"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(60 * 60 * 24, key_prefix="supplier_retrieve"))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    def _clear_cache(self):
        keys = cache.keys(f"*supplier*")
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

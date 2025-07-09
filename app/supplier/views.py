from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from app.base.pagination import CustomPagination
from app.base.mixins import (
    SoftDeleteViewSetMixin,
    ListCacheViewSetMixin,
    RetrieveCacheViewSetMixin,
)
from app.supplier import serializers
from app.supplier.filters import SupplierFilter
from app.supplier.models import Supplier


class SupplierModelViewSet(ModelViewSet,
                        SoftDeleteViewSetMixin,
                        ListCacheViewSetMixin, 
                        RetrieveCacheViewSetMixin):
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

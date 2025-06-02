from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from app.base.pagination import CustomPagination
from app.supplier import serializers
from app.supplier.models import Supplier


class SupplierModelViewSet(ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = serializers.SupplierSerializer
    pagination_class = CustomPagination
    filter_backends = [SearchFilter]
    search_fields = ['name', 'contact_phone_number', 'contact_email']

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

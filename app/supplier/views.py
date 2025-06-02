from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from app.base.pagination import CustomPagination
from app.supplier import serializers
from app.supplier.filters import SupplierFilter
from app.supplier.models import Supplier


DEFAULT_CACHE_TIME = 60 * 60 * 24


class SupplierModelViewSet(ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = serializers.SupplierSerializer
    pagination_class = CustomPagination
    filter_backends = [SearchFilter]
    filterset_class = SupplierFilter
    search_fields = ['name', 'contact_phone_number', 'contact_email']

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    
    def list(self, request, *args, **kwargs):
        _list_action = lambda req, *a, **k: super(SupplierModelViewSet, self).list(
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

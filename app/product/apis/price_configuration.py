from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from app.auth.permissions import IsInternalUser
from app.base.pagination import CustomPagination
from app.base.mixins import SoftDeleteViewSetMixin
from app.product import serializers
from app.product.models import ProductPriceConfiguration
from app.product.services.get_applied_price_configuration_product_service import GetAppliedPriceConfigurationProductService


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

    @action(detail=True, methods=['post'])
    def activate(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = True
        instance.save()
        
        instance.refresh_from_db()

        return Response(
            status=status.HTTP_200_OK,
            data=serializers.ProductPriceConfigurationSerializer(instance).data
        )

    @action(detail=True, methods=['post'])
    def deactivate(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()

        instance.refresh_from_db()

        return Response(
            status=status.HTTP_200_OK,
            data=serializers.ProductPriceConfigurationSerializer(instance).data
        )


class ProductPricePreviewAPIView(APIView):
    permission_classes = [IsInternalUser]

    def get(self, request):
        serializer = serializers.ProductPricePreviewRequestSerializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        product_ids = serializer.validated_data.get('product_ids')
        
        applied_product_prices = GetAppliedPriceConfigurationProductService(product_ids=product_ids).perform()
        
        serializer = serializers.ProductPricePreviewResponseSerializer(applied_product_prices.values(), many=True)
        
        paginator = CustomPagination()
        page = paginator.paginate_queryset(serializer.data, request)
        if page is not None:
            return paginator.get_paginated_response(serializer.data)
        
        return Response(
            data=serializer.data,
            status=status.HTTP_200_OK
        )

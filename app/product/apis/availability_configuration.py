from datetime import date
from django.forms import ValidationError
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter

from app.auth.permissions import IsInternalUser
from app.base.mixins import SoftDeleteViewSetMixin
from app.base.pagination import CustomPagination

from app.product import serializers
from app.product.models import ProductAvailabilityConfiguration
from app.product.services.schemas import ComputedProductAvailability
from app.product.services.get_product_availability_service import GetProductAvailabilityService
from app.product.services.block_product_availability import BlockProductAvailabilityService
from app.product.services.unblock_product_availability import UnblockProductAvailabilityService
from app.product.services.create_bulk_product_availability import CreateBulkProductAvailabilityConfigurationService


class ProductAvailabilityConfigurationModelViewSet(SoftDeleteViewSetMixin, ModelViewSet):
    queryset = ProductAvailabilityConfiguration.objects.filter(is_deleted=False)
    serializer_class = serializers.ProductAvailabilityConfigurationSerializer
    permission_classes = [IsInternalUser]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['code']
    ordering_fields = ['created_at', 'code', 'type', 'day']
    ordering = ['-created_at']


class CreateBulkProductAvailabilityConfigurationAPIView(APIView):
    permission_classes = [IsInternalUser]
    
    def post(self, request):
        serializer = serializers.CreateBulkProductAvailabilityConfigurationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        service = CreateBulkProductAvailabilityConfigurationService(
            product_ids=serializer.validated_data['product_ids'],
            start_date=serializer.validated_data['start_date'],
            end_date=serializer.validated_data['end_date'],
            type=serializer.validated_data['type'],
            value=serializer.validated_data['value'],
        )
        product_availability_configurations = service.perform()
        
        response = serializers.ProductAvailabilityConfigurationSerializer(product_availability_configurations, many=True)

        return Response(response.data, status=status.HTTP_200_OK)


class GetProductAvailabilityByDateRangeAPIView(APIView):
    permission_classes = [IsInternalUser]

    def get(self, request):
        serializer = serializers.GetAvailabilityCalendarRequestSerializer(data=request.query_params)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        service = GetProductAvailabilityService(
            product_ids=serializer.validated_data['product_ids'],
            start_date=serializer.validated_data['start_date'],
            end_date=serializer.validated_data['end_date'],
        )
        availability_by_day: dict[date, ComputedProductAvailability] = service.perform()
        
        availability_items = [
            {'date': day.strftime('%Y-%m-%d'), 'availabilities': availabilities}
            for day, availabilities in availability_by_day.items()
        ]

        serializer = serializers.ProductAvailabilityItemSerializer(availability_items, many=True)

        return Response({'data': serializer.data}, status=status.HTTP_200_OK)


class BlockProductAvailabilityAPIView(APIView):
    permission_classes = [IsInternalUser]

    def post(self, request):
        serializer = serializers.BlockProductAvailabilityRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        service = BlockProductAvailabilityService(
            product_ids=serializer.validated_data['product_ids'],
            start_date=serializer.validated_data['start_date'],
            end_date=serializer.validated_data['end_date'],
        )
        service.perform()

        return Response({'message': 'Product availability blocked successfully'}, status=status.HTTP_200_OK)
    
    
class UnblockProductAvailabilityAPIView(APIView):
    permission_classes = [IsInternalUser]

    def post(self, request):
        serializer = serializers.UnblockProductAvailabilityRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            service = UnblockProductAvailabilityService(
                product_ids=serializer.validated_data['product_ids'],
                start_date=serializer.validated_data['start_date'],
                end_date=serializer.validated_data['end_date'],
            )
            service.perform()
        except ValidationError as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Product availability unblocked successfully'}, status=status.HTTP_200_OK)

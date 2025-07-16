from datetime import date
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter

from app.auth.permissions import IsInternalUser
from app.base.mixins import SoftDeleteViewSetMixin
from app.base.pagination import CustomPagination
from app.core.utils.logger import logger

from app.product import serializers
from app.product.models import ProductAvailabilityConfiguration
from app.product.services.schemas import ComputedProductAvailability
from app.product.services.get_product_availability_service import GetProductAvailabilityService


class ProductAvailabilityConfigurationModelViewSet(SoftDeleteViewSetMixin, ModelViewSet):
    queryset = ProductAvailabilityConfiguration.objects.filter(is_deleted=False)
    serializer_class = serializers.ProductAvailabilityConfigurationSerializer
    permission_classes = [IsInternalUser]
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ['code', 'name']
    ordering_fields = [
        'created_at', 'code', 'name', 'type', 'start_date', 'end_date']
    ordering = ['-created_at']


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



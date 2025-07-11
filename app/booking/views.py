from django_filters.rest_framework import DjangoFilterBackend
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.filters import SearchFilter, OrderingFilter

from app.booking.models import (
    Booking, BookingStatus, BookingItem,
    BookingEventHistory, BookingInstanceTypeEnum,
)
from app.booking.serializers import (
    BookingSerializer,
    BookingItemSerializer,
    BookingEventHistorySerializer,
    AddBookingItemsPayloadSerializer,
    DeleteBookingItemsPayloadSerializer,
)
from app.product.models import ServiceType, Product
from app.base.pagination import CustomPagination
from app.payment.serializers import PaymentTransactionSerializer
from app.base.mixins import SoftDeleteViewSetMixin


class BookingModelViewSet(viewsets.ModelViewSet, SoftDeleteViewSetMixin):
    queryset = Booking.objects.filter(is_deleted=False)
    serializer_class = BookingSerializer
    pagination_class = CustomPagination
    lookup_field = 'code'
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    search_fields = ["code"]
    ordering_fields = [
        "code",
        "created_at",
        "status",
        "total_price",
        "total_guest"
    ]
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.action in ['create', 'retrieve', 'items', 'payment_transaction', 'event_histories', 'next_action']:
            return [AllowAny()]
        else:
            return [IsAuthenticated()]

    def get_queryset(self):
        if self.action in ['create', 'retrieve', 'items', 'payment_transaction', 'event_histories', 'next_action']:
            return super().get_queryset()
        else:
            if self.request.user.is_internal:
                return super().get_queryset()
            else:
                return super().get_queryset().filter(customer=self.request.user)

    @method_decorator(cache_page(60 * 60 * 24, key_prefix="booking_list"))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    @method_decorator(cache_page(60 * 60 * 24, key_prefix="booking_retrieve"))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def _clear_cache(self):
        keys = cache.keys(f"*booking*")
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

    @action(detail=True, methods=['get'], url_path='payment_transaction')
    def payment_transaction(self, request, *args, **kwargs):
        booking = self.get_object()
        payment_transactions = booking.payment_transactions.first()
        serializer = PaymentTransactionSerializer(payment_transactions)
        return Response({'data': serializer.data})

    @action(detail=True, methods=['post', 'get', 'delete'], url_path='items')
    def items(self, request, *args, **kwargs):
        if request.method == 'POST':
            return self.add_items(request, *args, **kwargs)
        elif request.method == 'GET':
            return self.get_items(request, *args, **kwargs)
        elif request.method == 'DELETE':
            return self.delete_items(request, *args, **kwargs)

    def add_items(self, request, *args, **kwargs):
        booking = self.get_object()
        serializer = AddBookingItemsPayloadSerializer(data=request.data, context={'booking': booking})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        booking_items = booking.bookingitem_set.all()
        booking.update_total_price()

        booking_items_serializer = BookingItemSerializer(booking_items, many=True)
        return Response({'data': booking_items_serializer.data}, status=status.HTTP_201_CREATED)

    def get_items(self, request, *args, **kwargs):
        booking = self.get_object()
        booking_items = booking.bookingitem_set.all()
        serializer = BookingItemSerializer(booking_items, many=True)
        return Response({'data': serializer.data})

    def delete_items(self, request, *args, **kwargs):
        booking = self.get_object()
        serializer = DeleteBookingItemsPayloadSerializer(data=request.data, context={'booking': booking})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        booking.update_total_price()

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], url_path='event_histories')
    def event_histories(self, request, *args, **kwargs):
        def get_unique_event_histories(event_histories):
            unique_event_histories = []
            unique_keys = []
            for event_history in event_histories:
                key = '_'.join([
                    str(event_history['event_type']),
                    str(event_history['instance_type']),
                    str(event_history['instance_id']),
                    str(event_history['description']),
                ])
                if key not in unique_keys:
                    unique_event_histories.append(event_history)
                    unique_keys.append(key)
            return unique_event_histories

        booking = self.get_object()
        event_histories = BookingEventHistory.objects.filter(
            instance_type=BookingInstanceTypeEnum.BOOKING,
            instance_id=str(booking.id),
        ).order_by('created_at')
        serializer = BookingEventHistorySerializer(event_histories, many=True)

        unique_event_histories = get_unique_event_histories(serializer.data)
        
        return Response({'data': unique_event_histories})

    @action(detail=True, methods=['get'], url_path='next_action')
    def next_action(self, request, *args, **kwargs):
        def get_service_types(booking):
            product_ids = booking.bookingitem_set.values_list('product', flat=True)
            service_types = Product.objects.filter(id__in=product_ids).values_list('service_type', flat=True).distinct()
            return service_types
        
        def get_next_action(current_status, service_types):
            if current_status == BookingStatus.NEW:
                return {
                    'action': 'pending_payment',
                    'description': 'Pending payment',
                }
            elif current_status == BookingStatus.PENDING_PAYMENT:
                return {
                    'action': 'purchase',
                    'description': 'Purchase booking',
                }
            elif current_status == BookingStatus.CONFIRMED:
                return {
                    'action': 'processing',
                    'description': 'Processing booking',
                }
            elif current_status == BookingStatus.PROCESSING and ServiceType.E_VISA in service_types:
                return {
                    'action': 'processing_by_government',
                    'description': 'Processing booking by government',
                }

        booking = self.get_object()
        service_types = get_service_types(booking)

        next_action = get_next_action(booking.status, service_types)

        return Response({'data': next_action}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel(self, request, *args, **kwargs):
        booking = self.get_object()

        try:
            booking.cancel()
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(status=status.HTTP_204_NO_CONTENT)


class BookingItemModelViewSet(viewsets.ModelViewSet):
    queryset = BookingItem.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = BookingItemSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        action = self.action
        if not action in ['retrieve', 'update', 'partial_update']:
            raise MethodNotAllowed(action)

        return super().get_queryset()

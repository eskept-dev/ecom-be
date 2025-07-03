from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed

from app import booking
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
from app.payment.models import PaymentTransactionStatus
from app.payment.serializers import PaymentTransactionSerializer


class BookingModelViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    pagination_class = CustomPagination
    lookup_field = 'code'

    def get_permissions(self):
        if self.action in ['create', 'retrieve', 'items', 'payment_transaction', 'event_histories', 'next_action']:
            return [AllowAny()]
        else:
            return [IsAuthenticated()]

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

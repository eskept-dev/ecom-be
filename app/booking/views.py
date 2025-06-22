from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.views import APIView

from app.booking.models import Booking, BookingItem, PaymentMethod
from app.booking.serializers import (
    BookingSerializer,
    BookingItemSerializer,
    AddBookingItemsPayloadSerializer,
    DeleteBookingItemsPayloadSerializer,
    PaymentMethodSerializer,
)
from app.base.pagination import CustomPagination


class BookingModelViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = BookingSerializer
    pagination_class = CustomPagination
    lookup_field = 'code'

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


class PaymentMethodApiView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        payment_methods = PaymentMethod.objects.filter(is_enabled=True)
        serializer = PaymentMethodSerializer(payment_methods, many=True)
        return Response({'data': serializer.data})
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import action

from app.booking.models import BookingStatus
from app.payment.serializers import (
    PaymentTransactionSerializer,
    PurchaseBookingSerializer,
)
from app.payment.models import (
    PaymentMethod,
    PaymentTransaction,
)
from app.payment.serializers import PaymentMethodSerializer
from app.payment.tasks import process_payment_task


class PaymentMethodAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        payment_methods = PaymentMethod.objects.filter(is_enabled=True)
        serializer = PaymentMethodSerializer(payment_methods, many=True)
        return Response(
            status=status.HTTP_200_OK,
            data={ 'data': serializer.data }
        )


class PaymentTransactionModelViewSet(viewsets.ModelViewSet):
    queryset = PaymentTransaction.objects.all()
    serializer_class = PaymentTransactionSerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        if self.action in ['retrieve', 'purchase']:
            return [AllowAny()]
        else:
            return [IsAuthenticated()]

    @action(detail=True, methods=['post'], url_path='purchase')
    def purchase(self, request, *args, **kwargs):
        payment_transaction = self.get_object()
        serializer = PurchaseBookingSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        booking = payment_transaction.booking
        if booking.status not in [BookingStatus.NEW, BookingStatus.PENDING_PAYMENT]:
            return Response({'error': 'Can not purchase this booking'}, status=status.HTTP_400_BAD_REQUEST)

        payment_transaction.purchase()
        payment_transaction.refresh_from_db()
        
        process_payment_task.delay(payment_transaction.id)

        return Response({ 'data': PaymentTransactionSerializer(payment_transaction).data }, status=status.HTTP_200_OK)

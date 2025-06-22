from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status

from app.payment.models import PaymentMethod
from app.payment.serializers import PaymentMethodSerializer


class PaymentMethodAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        payment_methods = PaymentMethod.objects.filter(is_enabled=True)
        serializer = PaymentMethodSerializer(payment_methods, many=True)
        return Response(
            status=status.HTTP_200_OK,
            data={ 'data': serializer.data }
        )

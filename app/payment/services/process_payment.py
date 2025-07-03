import time

from app.booking.models import (
    BookingEventHistory,
    BookingInstanceTypeEnum,
    BookingEventTypeEnum,
)
from app.payment.models import PaymentTransaction


def process_payment(payment_transaction_id):    
    try:
        payment_transaction = PaymentTransaction.objects.get(id=payment_transaction_id)
    except PaymentTransaction.DoesNotExist:
        raise Exception('Payment transaction not found')

    if payment_transaction.is_pending():
        time.sleep(3)
        payment_transaction.purchase_success()

        BookingEventHistory.objects.create(
            event_type=BookingEventTypeEnum.PURCHASE,
            instance_type=BookingInstanceTypeEnum.BOOKING,
            instance_id=str(payment_transaction.booking.id),
            trigger_by=payment_transaction.booking.customer,
            value={
                'payment_transaction': {
                    'id': str(payment_transaction.id),
                    'status': payment_transaction.status,
                    'amount': payment_transaction.amount,
                    'currency': payment_transaction.currency,
                    'payment_method_type': payment_transaction.payment_method_type,
                },
            },
        )
    else:
        raise Exception('Can not process payment transaction')

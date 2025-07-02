import time

from app.payment.models import (
    PaymentTransaction,
    PaymentTransactionStatus,
)

def process_payment(payment_transaction_id):    
    try:
        payment_transaction = PaymentTransaction.objects.get(id=payment_transaction_id)
    except PaymentTransaction.DoesNotExist:
        raise Exception('Payment transaction not found')

    if payment_transaction.is_pending():
        time.sleep(3)
        payment_transaction.purchase_success()
    else:
        raise Exception('Can not process payment transaction')

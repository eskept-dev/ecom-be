from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from app.core.utils.logger import logger

from app.booking.models import Booking
from app.payment.models import PaymentMethodType, PaymentTransaction


@receiver(post_save, sender=Booking)
def create_payment_transaction(sender, instance, created, **kwargs):
    def init_payment_transaction():
        PaymentTransaction.objects.create(
            booking=instance,
            amount=instance.total_price,
            currency=instance.currency,
            payment_method_type=PaymentMethodType.CREDIT_CARD,
        )

    def update_payment_transaction():
        payment_transaction = PaymentTransaction.objects.get(booking=instance)
        payment_transaction.amount = instance.total_price
        payment_transaction.currency = instance.currency
        payment_transaction.save()

    if created:
        init_payment_transaction()
    else:
        update_payment_transaction()

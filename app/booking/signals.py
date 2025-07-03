from django.db.models.signals import post_save
from django.dispatch import receiver

from app.booking.models import (
    Booking,
    BookingEventHistory,
    BookingInstanceTypeEnum,
    BookingEventTypeEnum,
    BookingStatus,
)
from app.payment.models import PaymentMethodType, PaymentTransaction
from app.booking.services.create_booking_customer import create_booking_customer


@receiver(post_save, sender=Booking)
def create_payment_transaction(sender, instance, created, **kwargs):
    def init_payment_transaction():
        PaymentTransaction.objects.create(
            booking=instance,
            amount=instance.total_price,
            currency=instance.currency,
            payment_method_type=PaymentMethodType.CREDIT_CARD,
        )

    def init_booking_history(customer):
        BookingEventHistory.objects.create(
            event_type=BookingEventTypeEnum.CREATE,
            instance_type=BookingInstanceTypeEnum.BOOKING,
            instance_id=str(instance.id),
            trigger_by=customer,
        )
        
    def add_booking_history(booking, description):
        BookingEventHistory.objects.create(
            event_type=BookingEventTypeEnum.UPDATE,
            instance_type=BookingInstanceTypeEnum.BOOKING,
            instance_id=str(booking.id),
            trigger_by=booking.customer,
            description=description,
        )

    def update_payment_transaction():
        payment_transaction = PaymentTransaction.objects.get(booking=instance)
        if (payment_transaction.amount != instance.total_price) or (payment_transaction.currency != instance.currency):
            payment_transaction.amount = instance.total_price
            payment_transaction.currency = instance.currency
            payment_transaction.save()
            
    def handle_paid_booking():
        if instance.status == BookingStatus.PAID:
            instance.status = BookingStatus.CONFIRMED
            instance.save()
            add_booking_history(instance, f'Booking status updated to {instance.status}')

    if created:
        init_payment_transaction()
        customer = create_booking_customer(instance.id)
        init_booking_history(customer)
    else:
        update_payment_transaction()
        handle_paid_booking()        

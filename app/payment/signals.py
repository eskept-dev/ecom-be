from django.db.models.signals import post_save
from django.dispatch import receiver

from app.booking.models import BookingEventHistory, BookingInstanceTypeEnum, BookingEventTypeEnum, BookingStatus
from app.payment.models import PaymentTransaction, PaymentTransactionStatus


@receiver(post_save, sender=PaymentTransaction)
def update_booking_status(sender, instance, created, **kwargs):
    def add_booking_history(booking, description):
        BookingEventHistory.objects.create(
            event_type=BookingEventTypeEnum.UPDATE,
            instance_type=BookingInstanceTypeEnum.BOOKING,
            instance_id=str(booking.id),
            trigger_by=booking.customer,
            description=description,
        )

    def update_booking_status():
        if payment_transaction.status == PaymentTransactionStatus.PENDING:
            booking.status = BookingStatus.PENDING_PAYMENT
            booking.save()
            add_booking_history(booking, f'Booking status updated to {booking.status}')
        elif payment_transaction.status == PaymentTransactionStatus.SUCCESS:
            booking.status = BookingStatus.PAID
            booking.save()
            add_booking_history(booking, f'Booking status updated to {booking.status}')
        elif payment_transaction.status == PaymentTransactionStatus.FAILED:
            booking.status = BookingStatus.FAILED
            booking.save()
            add_booking_history(booking, f'Failed to purchase booking')
        elif payment_transaction.status == PaymentTransactionStatus.CANCELLED:
            booking.status = BookingStatus.CANCELLED
            booking.save()
            add_booking_history(booking, f'Cancelled payment transaction')

    payment_transaction = instance
    booking = payment_transaction.booking
    
    if not created:
        update_booking_status()

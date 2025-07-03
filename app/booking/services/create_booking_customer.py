from app.core.utils.logger import logger
from app.booking.models import Booking
from app.user.models import User


def create_booking_customer(booking_id):
    booking = Booking.objects.filter(id=booking_id).first()
    if not booking:
        raise Exception('Booking not found')
    
    if booking.customer:
        return booking.customer

    customer_email = booking.contact_info.get('email')
    if not customer_email:
        raise Exception('Customer email is required')
    
    try:
        customer = User.objects.filter(email=customer_email).first()
        if not customer:
            customer = User.objects.create(email=customer_email)

        booking.customer = customer
        booking.save()
    except Exception as e:
        logger.error(f'Can not create customer: {e}')
        raise Exception('Can not create customer')

    return customer

import uuid
from datetime import datetime
from django.db import models

from app.base.models import BaseModel
from app.product.models import Currency, Product
from app.user.models import User


CONTACT_INFO_REQUIRED_FIELDS = [
    'full_name',
    'phone_number',
    'email',
]
GUEST_INFO_REQUIRED_FIELDS = [
    'full_name',
    'phone_number',
    'email',
]


class BookingStatus(models.TextChoices):
    NEW = 'new'
    CONFIRMED = 'confirmed'
    PENDING_PAYMENT = 'pending_payment'
    PAID = 'paid'
    PROCESSING = 'processing'
    PROCESSING_BY_GOVERNMENT = 'processing_by_government'
    REJECTED = 'rejected'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'


class Booking(BaseModel):
    PREFIX_CODE = 'BK'

    code = models.CharField(max_length=16, unique=True)
    status = models.CharField(max_length=32, choices=BookingStatus.choices, default=BookingStatus.NEW)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)

    currency = models.CharField(max_length=3, choices=Currency.choices, default=Currency.VND)
    total_price = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    total_guest = models.IntegerField(default=1)
    total_luggage = models.IntegerField(default=0)
    note = models.TextField(blank=True, null=True)

    # booking detail
    is_self_booking = models.BooleanField(default=True)
    contact_info = models.JSONField(default=dict)
    guest_info = models.JSONField(default=dict)
    details = models.JSONField(default=dict)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_unique_code()
            
        if not self.validate():
            raise ValueError('Invalid data')
            
        return super().save(*args, **kwargs)

    def generate_unique_code(self):
        # code = BK + YYMMDD + 4 digits
        # example: BK2506170001
        today = datetime.now().strftime('%y%m%d')
        last_booking = Booking.objects.filter(code__startswith=f'{self.PREFIX_CODE}{today}').order_by('-code').first()
        if last_booking:
            last_booking_number = int(last_booking.code.split(f'{self.PREFIX_CODE}{today}')[1])
            new_booking_number = last_booking_number + 1
        else:
            new_booking_number = 1
        return f'{self.PREFIX_CODE}{today}{new_booking_number:04d}'

    def validate(self):
        if self.contact_info and not self.validate_booking_detail_section(self.contact_info, CONTACT_INFO_REQUIRED_FIELDS):
            return False

        if self.guest_info and not self.validate_booking_detail_section(self.guest_info, GUEST_INFO_REQUIRED_FIELDS):
            return False
        
        return True

    @staticmethod
    def validate_booking_detail_section(value, required_fields):
        for field in required_fields:
            if field not in value:
                return False
        return True

    def update_total_price(self):
        booking_items = self.bookingitem_set.all()
        if not booking_items.exists():
            self.total_price = 0
        else:
            self.total_price = sum(item.total for item in booking_items)
        self.save()


class BookingItem(BaseModel):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    due_datetime = models.DateTimeField(null=True, blank=True)

    index = models.IntegerField(default=0)
    quantity = models.IntegerField()

    price = models.DecimalField(max_digits=16, decimal_places=2)
    total = models.DecimalField(max_digits=16, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total = self.price * self.quantity

        if not self.index:
            self.index = self.get_index()

        return super().save(*args, **kwargs)

    def get_index(self):
        return self.booking.bookingitem_set.filter(index__lt=self.index).count() + 1


class BookingEventHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    trigger_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_system = models.BooleanField(default=False)

    event_type = models.CharField(max_length=128)
    message = models.TextField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)

import uuid
from django.db import models

from app.base.models import BaseModel
from app.product.models import Product
from app.user.models import User


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


class PaymentType(models.TextChoices):
    CREDIT_CARD = 'credit_card'
    BANK_TRANSFER = 'bank_transfer'
    CASH = 'cash'


class PaymentMethod(BaseModel):
    type = models.CharField(max_length=32, choices=PaymentType.choices, unique=True)
    description = models.TextField(blank=True, null=True)
    is_enabled = models.BooleanField(default=True)


class Booking(BaseModel):
    status = models.CharField(max_length=32, choices=BookingStatus.choices, default=BookingStatus.NEW)
    payment_type = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)
    customer = models.ForeignKey(User, on_delete=models.CASCADE)

    total_price = models.DecimalField(max_digits=16, decimal_places=2)
    total_guest = models.IntegerField()
    total_luggage = models.IntegerField()
    note = models.TextField(blank=True, null=True)

    # booking detail
    is_self_booking = models.BooleanField(default=True)    
    contact_info = models.JSONField()
    guest_info = models.JSONField()
    details = models.JSONField()


class BookingItem(BaseModel):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    due_datetime = models.DateTimeField(null=True, blank=True)

    index = models.IntegerField(default=1)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=16, decimal_places=2)
    total = models.DecimalField(max_digits=16, decimal_places=2)


class BookingEventHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    trigger_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_system = models.BooleanField(default=False)

    event_type = models.CharField(max_length=128)
    message = models.TextField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)

from django.db import models

from app.booking.models import Booking
from app.base.models import BaseModel


class PaymentMethodType(models.TextChoices):
    CREDIT_CARD = 'credit_card'
    BANK_TRANSFER = 'bank_transfer'
    CASH = 'cash'


class PaymentTransactionStatus(models.TextChoices):
    NEW = 'new'
    PENDING = 'pending'
    SUCCESS = 'success'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


class PaymentMethod(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    type = models.CharField(max_length=32, choices=PaymentMethodType.choices, unique=True, primary_key=True)
    description = models.TextField(blank=True, null=True)
    is_enabled = models.BooleanField(default=True)


class PaymentTransaction(BaseModel):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="payment_transactions")
    status = models.CharField(
        max_length=32,
        choices=PaymentTransactionStatus.choices,
        default=PaymentTransactionStatus.NEW,
    )
    payment_method_type = models.CharField(
        max_length=32,
        choices=PaymentMethodType.choices,
        db_column='payment_method_type',
        default=PaymentMethodType.CREDIT_CARD,
    )

    transaction_code = models.CharField(max_length=64, blank=True, null=True)
    transaction_time = models.DateTimeField(blank=True, null=True)
    success_time = models.DateTimeField(blank=True, null=True)

    amount = models.DecimalField(max_digits=16, decimal_places=2)
    currency = models.CharField(max_length=8, default='VND')

    buyer_name = models.CharField(max_length=128, blank=True, null=True)
    buyer_email = models.EmailField(blank=True, null=True)
    buyer_phone = models.CharField(max_length=20, blank=True, null=True)
    buyer_address = models.CharField(max_length=255, blank=True, null=True)
    buyer_city = models.CharField(max_length=128, blank=True, null=True)
    buyer_country = models.CharField(max_length=128, blank=True, null=True)

    installment = models.BooleanField(default=False)
    installment_month = models.IntegerField(blank=True, null=True)
    bank_code = models.CharField(max_length=32, blank=True, null=True)
    bank_name = models.CharField(max_length=128, blank=True, null=True)
    card_number = models.CharField(max_length=32, blank=True, null=True)

    payer_fee = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)
    merchant_fee = models.DecimalField(max_digits=16, decimal_places=2, blank=True, null=True)

    description = models.TextField(blank=True, null=True)
    reason = models.TextField(blank=True, null=True)
    authen_code = models.CharField(max_length=64, blank=True, null=True)
    bank_type = models.CharField(max_length=32, blank=True, null=True)

    signature = models.TextField(blank=True, null=True)
    checksum = models.TextField(blank=True, null=True)

    request_payload = models.JSONField(blank=True, null=True)
    response_payload = models.JSONField(blank=True, null=True)
    webhook_payload = models.JSONField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.booking.code} - {self.payment_method_type}"
    
    def is_new(self):
        return self.status == PaymentTransactionStatus.NEW
    
    def is_pending(self):
        return self.status == PaymentTransactionStatus.PENDING
    
    def is_success(self):
        return self.status == PaymentTransactionStatus.SUCCESS
    
    def is_failed(self):
        return self.status == PaymentTransactionStatus.FAILED
    
    def is_cancelled(self):
        return self.status == PaymentTransactionStatus.CANCELLED

    def purchase(self):
        self.status = PaymentTransactionStatus.PENDING
        self.save()
        
    def purchase_success(self):
        self.status = PaymentTransactionStatus.SUCCESS
        self.save()
        
    def purchase_failed(self):
        self.status = PaymentTransactionStatus.FAILED
        self.save()
        
    def purchase_cancelled(self):
        self.status = PaymentTransactionStatus.CANCELLED
        self.save()

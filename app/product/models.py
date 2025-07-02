from django.db import models

from app.base.models import BaseModel
from app.core.utils.string import slugify
from app.supplier.models import Supplier


class ServiceType(models.TextChoices):
    AIRPORT_TRANSFER = 'airport_transfer'
    FAST_TRACK = 'fast_track'
    E_VISA = 'e_visa'


class Currency(models.TextChoices):
    VND = 'vnd'
    USD = 'usd'


class ProductStatus(models.TextChoices):
    ACTIVE = 'active'
    INACTIVE = 'inactive'


class ProductUnit(models.TextChoices):
    ROUND = 'round'
    PERSON = 'person'


class Product(BaseModel):
    name = models.CharField(max_length=255)
    code_name = models.CharField(max_length=255, unique=True)
    status = models.CharField(
        max_length=20, choices=ProductStatus.choices, default=ProductStatus.ACTIVE)
    service_type = models.CharField(max_length=20, choices=ServiceType.choices)

    available_locations = models.JSONField(default=list, null=True, blank=True)

    image_url = models.URLField(null=True, blank=True)
    unit = models.CharField(max_length=20, choices=ProductUnit.choices)

    price_vnd = models.DecimalField(max_digits=10, decimal_places=2)
    price_usd = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.DecimalField(max_digits=3, decimal_places=2)
    review_count = models.IntegerField(default=0)

    details = models.JSONField(default=dict, null=True, blank=True)
    highlights = models.JSONField(default=list, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    cancellation_policy = models.TextField(null=True, blank=True)
    what_nexts = models.JSONField(default=list, null=True, blank=True)

    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    def generate_unique_code_name(self):
        return slugify(self.name)

    def save(self, *args, **kwargs):
        self.code_name = self.generate_unique_code_name()
        super().save(*args, **kwargs)

    @property
    def is_active(self):
        return self.status == ProductStatus.ACTIVE
    
    def get_price_vnd(self):
        return self.price_vnd
    
    def get_price_usd(self):
        return self.price_usd
    
    def get_price(self, currency):
        if currency == Currency.VND:
            return self.price_vnd
        elif currency == Currency.USD:
            return self.price_usd
        else:
            raise ValueError(f'Invalid currency: {currency}')

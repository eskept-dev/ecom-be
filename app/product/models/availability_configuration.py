from datetime import datetime
import random

from django.db import models
from django.forms import ValidationError
from django.utils import timezone

from app.base.models import BaseModel, SoftDeleteMixin  


class ProductAvailabilityConfigurationType(models.TextChoices):
    BLOCK = "block"
    NO_LIMIT = "no_limit"
    FIXED_QUANTITY = "fixed_quantity"
    PERCENTAGE_QUANTITY = "percentage_quantity"


class ProductAvailabilityConfiguration(BaseModel, SoftDeleteMixin):
    NO_LIMIT_MAX_CAPACITY = 9999999999

    product = models.ForeignKey("Product", related_name="availability_configs", on_delete=models.CASCADE)

    type = models.CharField(max_length=255, choices=ProductAvailabilityConfigurationType.choices)
    value = models.IntegerField(default=0)
    day = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
        self.validate()
        super().save(*args, **kwargs)
    
    def validate(self):
        if self.type == ProductAvailabilityConfigurationType.FIXED_QUANTITY:
            self.validate_fixed_quantity()
        elif self.type == ProductAvailabilityConfigurationType.PERCENTAGE_QUANTITY:
            self.validate_percentage_quantity()

    def validate_fixed_quantity(self):
        if self.value is None:
            raise ValidationError("Value is required")
        
        if self.value <= 0:
            raise ValidationError("Value must be greater than 0")

    def validate_percentage_quantity(self):
        if self.value is None:
            raise ValidationError("Value is required")
        
        if self.value < 0 or self.value > 100:
            raise ValidationError("Value must be between 0 and 100")

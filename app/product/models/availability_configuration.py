from datetime import timezone, datetime

from django.db import models
from django.forms import ValidationError

from app.base.models import BaseModel, SoftDeleteMixin  


class ProductAvailabilityConfigurationType(models.TextChoices):
    BLOCK = "block"
    NO_LIMIT = "no_limit"
    FIXED_QUANTITY = "fixed_quantity"
    PERCENTAGE_QUANTITY = "percentage_quantity"


class ProductAvailabilityConfiguration(BaseModel, SoftDeleteMixin):
    PREFIX_CODE = 'AC'
    NO_LIMIT_MAX_CAPACITY = 9999999999
    
    name = models.CharField(max_length=255, null=True, blank=True)
    code = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)
    
    products = models.ManyToManyField("Product", related_name="availability_configs", blank=True)

    type = models.CharField(max_length=255, choices=ProductAvailabilityConfigurationType.choices)
    value = models.JSONField(null=True, blank=True)

    start_date = models.DateField()
    end_date = models.DateField()

    def save(self, *args, **kwargs):
        self.validate()
        
        if not self.code:
            self.code = self.generate_unique_code()

        super().save(*args, **kwargs)
    
    def generate_unique_code(self):
        # code = AC + YYMMDD + 4 digits
        # example: AC2506170001
        today = datetime.now().strftime('%y%m%d')
        last_availability_configuration = ProductAvailabilityConfiguration.objects.filter(code__startswith=f'{self.PREFIX_CODE}{today}').order_by('-code').first()
        if last_availability_configuration:
            last_availability_configuration_number = int(last_availability_configuration.code.split(f'{self.PREFIX_CODE}{today}')[1])
            new_availability_configuration_number = last_availability_configuration_number + 1
        else:
            new_availability_configuration_number = 1
        return f'{self.PREFIX_CODE}{today}{new_availability_configuration_number:04d}'
    
    def validate(self):
        self.validate_time_range()
        
        if self.type == ProductAvailabilityConfigurationType.FIXED_QUANTITY:
            self.validate_fixed_quantity()
        elif self.type == ProductAvailabilityConfigurationType.PERCENTAGE_QUANTITY:
            self.validate_percentage_quantity()
    
    def validate_time_range(self):
        if self.start_date is None or self.end_date is None:
            raise ValidationError("Start date and end date are required")
        
        if self.start_date > self.end_date:
            raise ValidationError("Start date must be before end date")
    
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

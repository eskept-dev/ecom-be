from datetime import timezone, datetime

from django.db import models

from app.base.models import BaseModel, SoftDeleteMixin  


class PriceAdjustmentType(models.TextChoices):
    FIXED = "fixed"
    PERCENTAGE = "percentage"
    

class PriceAdjustmentTimeRangeType(models.TextChoices):
    PERIOD = "period"
    RECURRING_DAY_OF_WEEK = "recurring_day_of_week"
    RECURRING_DAY_OF_MONTH = "recurring_day_of_month"


class PriceAdjustmentRecurringType(models.TextChoices):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class ProductPriceConfiguration(BaseModel, SoftDeleteMixin):
    PREFIX_CODE = 'PC'

    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)

    products = models.ManyToManyField("Product", related_name="price_configs", blank=True)

    # adjustment value
    adjustment_type = models.CharField(
        max_length=32,
        choices=PriceAdjustmentType.choices,
        default=PriceAdjustmentType.FIXED,
    )

    adjustment_value = models.JSONField(null=True, blank=True)

    # time range
    time_range_type = models.CharField(
        max_length=32,
        choices=PriceAdjustmentTimeRangeType.choices,
        default=PriceAdjustmentTimeRangeType.PERIOD,
    )
    time_range_value = models.JSONField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_unique_code()
            
        self.validate()
    
        return super().save(*args, **kwargs)

    def generate_unique_code(self):
        # code = PC + YYMMDD + 4 digits
        # example: PC2506170001
        today = datetime.now().strftime('%y%m%d')
        last_price_configuration = ProductPriceConfiguration.objects.filter(code__startswith=f'{self.PREFIX_CODE}{today}').order_by('-code').first()
        if last_price_configuration:
            last_price_configuration_number = int(last_price_configuration.code.split(f'{self.PREFIX_CODE}{today}')[1])
            new_price_configuration_number = last_price_configuration_number + 1
        else:
            new_price_configuration_number = 1
        return f'{self.PREFIX_CODE}{today}{new_price_configuration_number:04d}'
    
    def validate(self):
        if self.adjustment_type == PriceAdjustmentType.FIXED:
            if not self.adjustment_value:
                raise ValueError('Adjustment value is required')
        elif self.adjustment_type == PriceAdjustmentType.PERCENTAGE:
            if not self.adjustment_value:
                raise ValueError('Adjustment value is required')
            
        if self.time_range_type == PriceAdjustmentTimeRangeType.PERIOD:
            if not self.validate_time_range_period():
                raise ValueError('Start datetime and end datetime are required')
        elif self.time_range_type == PriceAdjustmentTimeRangeType.RECURRING_DAY_OF_WEEK \
                or self.time_range_type == PriceAdjustmentTimeRangeType.RECURRING_DAY_OF_MONTH:
            if not self.validate_time_range_recurring():
                raise ValueError('Time range value is required')

        return True
    
    def validate_time_range_period(self):
        return True
    
    def validate_time_range_recurring(self):
        if not self.time_range_value:
            raise ValueError('Time range value is required')

        return True

    def can_apply(self, product):
        if not self.is_active:
            return False
        
        if not self.is_validated_time_range():
            return False

        if self.products.count() > 0 and product not in self.products.all():
            return False

        return True

    def is_validated_time_range_recurring(self):
        if not self.time_range_value:
            return False
        
        if self.time_range_value.get('type') not in PriceAdjustmentRecurringType.values:
            return False
        

    def is_validated_time_range_period(self):
        if not self.time_range_value:
            return True

        if self.time_range_value.get('start_datetime') and self.time_range_value.get('end_datetime'):
            now = timezone.now()
            return (self.time_range_value.get('start_datetime') <= now <= self.time_range_value.get('end_datetime'))

        if self.time_range_value.get('start_datetime'):
            now = timezone.now()
            return self.time_range_value.get('start_datetime') <= now

        return False

from datetime import timezone, datetime

from django.db import models

from app.base.models import BaseModel, SoftDeleteMixin  
from app.base.enums import BaseEnum


class PriceAdjustmentType(models.TextChoices):
    FIXED = "fixed"
    PERCENTAGE = "percentage"
    

class PriceAdjustmentTimeRangeType(models.TextChoices):
    PERIOD = "period"
    RECURRING_DAY_OF_WEEK = "recurring_day_of_week"
    RECURRING_DAY_OF_MONTH = "recurring_day_of_month"


class DayOfWeek(BaseEnum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


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
        self._validate_adjustment()
        self._validate_time_range()

    def is_time_range_valid(self) -> bool:
        if self.time_range_type == PriceAdjustmentTimeRangeType.PERIOD:
            return self._verify_time_range_period()
        elif self.time_range_type == PriceAdjustmentTimeRangeType.RECURRING_DAY_OF_WEEK:
            return self._verify_time_range_recurring_day_of_week()
        elif self.time_range_type == PriceAdjustmentTimeRangeType.RECURRING_DAY_OF_MONTH:
            return self._verify_time_range_recurring_day_of_month()

    def is_valid_products(self, product_id: int) -> bool:
        if not self.products.all(): return True
        
        return self.products.filter(id=product_id).exists()

    def can_apply_to_product(self, product_id: int) -> bool:
        return self.is_valid_products(product_id) and self.is_time_range_valid()

    def _validate_adjustment(self):
        if self.adjustment_type == PriceAdjustmentType.FIXED:
            self._validate_adjustment_fixed()
        elif self.adjustment_type == PriceAdjustmentType.PERCENTAGE:
            self._validate_adjustment_percentage()
        else:
            raise ValueError('Invalid adjustment type')

    def _validate_adjustment_fixed(self):
        if not self.adjustment_value:
            raise ValueError('Adjustment value is required')
        
        if not isinstance(self.adjustment_value, dict):
            raise ValueError('Invalid fixed adjustment value')
        
        fixed_vnd = self.adjustment_value.get('fixed_vnd')
        fixed_usd = self.adjustment_value.get('fixed_usd')
        
        if not fixed_vnd and not fixed_usd:
            raise ValueError('fixed_vnd or fixed_usd is required')
        
        if fixed_vnd and not isinstance(fixed_vnd, (int, float)):
            raise ValueError('fixed_vnd must be a number')
        
        if fixed_usd and not isinstance(fixed_usd, (int, float)):
            raise ValueError('fixed_usd must be a number')
        
        if fixed_vnd < 0 or fixed_usd < 0:
            raise ValueError('fixed_vnd and fixed_usd must be greater than 0')
        
    def _validate_adjustment_percentage(self):
        if not self.adjustment_value:
            raise ValueError('Adjustment value is required')
        
        if not isinstance(self.adjustment_value, dict):
            raise ValueError('Invalid percentage adjustment value')
        
        percentage = self.adjustment_value.get('percentage')
        if not percentage:
            raise ValueError('percentage is required')
        
        if not isinstance(percentage, (int, float)):
            raise ValueError('percentage must be a number')
        
        if percentage < 0 or percentage > 100:
            raise ValueError('percentage must be between 0 and 100')
            
    def _validate_time_range(self):
        if self.time_range_type == PriceAdjustmentTimeRangeType.PERIOD:
            self._validate_time_range_period()
        elif self.time_range_type == PriceAdjustmentTimeRangeType.RECURRING_DAY_OF_WEEK:
            self._validate_time_range_recurring_day_of_week()
        elif self.time_range_type == PriceAdjustmentTimeRangeType.RECURRING_DAY_OF_MONTH:
            self._validate_time_range_recurring_day_of_month()
    
    def _validate_time_range_period(self):
        if not self.time_range_value:
            raise ValueError('Time range value is required')
        
        if not isinstance(self.time_range_value, dict):
            raise ValueError('Invalid time range value')
        
        if not self.time_range_value.get('start_datetime') and not self.time_range_value.get('end_datetime'):
            raise ValueError('Start datetime and end datetime are required')
    
    def _validate_time_range_recurring_day_of_week(self):
        if not self.time_range_value:
            raise ValueError('Time range value is required')

        if not isinstance(self.time_range_value, dict):
            raise ValueError('Invalid time range value')
        
        day_of_week = self.time_range_value.get('day_of_week')
        if not day_of_week:
            raise ValueError('Day of week is required')
        
        if not isinstance(day_of_week, list):
            raise ValueError('Day of week must be a list')
        
        for day in day_of_week:
            if day not in DayOfWeek.choices():
                raise ValueError('Invalid day of week')

    def _validate_time_range_recurring_day_of_month(self):
        if not self.time_range_value:
            raise ValueError('Time range value is required')
        
        if not isinstance(self.time_range_value, dict):
            raise ValueError('Invalid time range value')
        
        day_of_month = self.time_range_value.get('day_of_month')
        if not day_of_month:
            raise ValueError('Day of month is required')
        
        if not isinstance(day_of_month, int):
            raise ValueError('Day of month must be a number')
        
        if day_of_month < 1 or day_of_month > 31:
            raise ValueError('Day of month must be between 1 and 31')

    def _verify_time_range_period(self) -> bool:
        if not isinstance(self.time_range_value, dict):
            return False
        
        start_date = self.time_range_value.get('start_date')
        end_date = self.time_range_value.get('end_date')
        
        # if no time range, it means the price configuration is always valid
        if not start_date or not end_date:
            return True
        
        if start_date and end_date:
            return start_date <= datetime.now() <= end_date
        elif start_date:
            return start_date <= datetime.now()
        elif end_date:
            return datetime.now() <= end_date

        return True

    def _verify_time_range_recurring_day_of_week(self) -> bool:
        if not isinstance(self.time_range_value, list):
            return False
        
        day_of_week_list = self.time_range_value
        
        for day_of_week in day_of_week_list:   
            if day_of_week not in DayOfWeek.choices(): 
                return False

        now = datetime.now()
        return now.weekday() in day_of_week_list

    def _verify_time_range_recurring_day_of_month(self) -> bool:
        if not isinstance(self.time_range_value, list):
            return False
        
        day_of_month_list = self.time_range_value
        
        for day_of_month in day_of_month_list:
            if day_of_month < 1 or day_of_month > 31:
                return False

        now = datetime.now()
        return now.day in day_of_month_list

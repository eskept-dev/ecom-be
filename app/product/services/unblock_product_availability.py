from datetime import date

from rest_framework.exceptions import ValidationError

from app.base.service import BaseService
from app.product.models import (
    ProductAvailabilityConfiguration,
    ProductAvailabilityConfigurationType,
)


class UnblockProductAvailabilityService(BaseService):
    def __init__(self, product_ids: list[int], start_date: date, end_date: date):
        self.product_ids = product_ids
        self.start_date = start_date
        self.end_date = end_date

    def perform(self):
        block_configurations = ProductAvailabilityConfiguration.objects.filter(
            products__id__in=self.product_ids,
            type=ProductAvailabilityConfigurationType.BLOCK,
            start_date__lte=self.start_date,
            end_date__gte=self.end_date,
        )

        if block_configurations.count() == 0:
            raise ValidationError("Products are not blocked for the given date range")
        
        for config in block_configurations:
            config.products.remove(self.product_ids)
            config.save()

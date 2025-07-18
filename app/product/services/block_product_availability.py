from datetime import date, timedelta

from app.base.service import BaseService
from app.product.models import (
    ProductAvailabilityConfiguration,
    ProductAvailabilityConfigurationType,
)


class BlockProductAvailabilityService(BaseService):
    def __init__(self, product_ids: list[int], start_date: date, end_date: date):
        self.product_ids = product_ids
        self.start_date = start_date
        self.end_date = end_date

    def perform(self):
        self.clean_up_existing_configurations()

        self.block_product_availability()
    
    def clean_up_existing_configurations(self):
        ProductAvailabilityConfiguration.objects.filter(
            product_id__in=self.product_ids,
            day__gte=self.start_date,
            day__lte=self.end_date,
        ).delete()
        
    def block_product_availability(self):
        bulk = []
        
        for product_id in self.product_ids:
            day = self.start_date
            while day <= self.end_date:
                bulk.append(ProductAvailabilityConfiguration(
                    product_id=product_id,
                    day=day,
                    type=ProductAvailabilityConfigurationType.BLOCK,
                ))
                day += timedelta(days=1)

        ProductAvailabilityConfiguration.objects.bulk_create(bulk)

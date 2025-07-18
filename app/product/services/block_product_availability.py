from datetime import date, timedelta

from app.base.service import BaseService
from app.product.models import (
    ProductAvailabilityConfiguration,
    ProductAvailabilityConfigurationType,
    Product,
)


class BlockProductAvailabilityService(BaseService):
    def __init__(self, product_ids: list[int], start_date: date, end_date: date):
        self.product_ids = product_ids
        self.start_date = start_date
        self.end_date = end_date
        
    def perform(self):
        if self.product_ids:
            self.block_by_product_ids()
        else:
            self.block_by_time_range()

    def block_by_product_ids(self):
        self.clean_up_by_product_ids()

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

    def block_by_time_range(self):
        self.clean_up_by_time_range()
        
        self.product_ids = Product.objects.filter(is_deleted=False).values_list('id', flat=True)

        self.block_product_availability()

    def clean_up_by_time_range(self):
        ProductAvailabilityConfiguration.objects.filter(
            day__gte=self.start_date,
            day__lte=self.end_date,
        ).delete()

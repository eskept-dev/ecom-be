from datetime import timedelta
from app.base.service import BaseService
from app.product.models import ProductAvailabilityConfiguration


class CreateBulkProductAvailabilityConfigurationService(BaseService):
    def __init__(self, product_ids, start_date, end_date, type, value):
        self.product_ids = product_ids
        self.start_date = start_date
        self.end_date = end_date
        self.type = type
        self.value = value

    def perform(self):
        self.clean_up()

        return self.create_bulk()

    def clean_up(self):
        ProductAvailabilityConfiguration.objects.filter(
            product_id__in=self.product_ids,
            day__gte=self.start_date,
            day__lte=self.end_date,
        ).delete()
        
    def create_bulk(self):
        bulk_create_items = []
        for product_id in self.product_ids:
            day = self.start_date
            while day <= self.end_date:
                bulk_create_items.append(
                    ProductAvailabilityConfiguration(
                        product_id=product_id,
                        day=day,
                        type=self.type,
                        value=self.value,
                    )
                )
                day += timedelta(days=1)
        ProductAvailabilityConfiguration.objects.bulk_create(bulk_create_items)
        return bulk_create_items

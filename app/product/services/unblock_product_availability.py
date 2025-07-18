from datetime import date

from app.base.service import BaseService
from app.product.models import ProductAvailabilityConfiguration


class UnblockProductAvailabilityService(BaseService):
    def __init__(self, product_ids: list[int], start_date: date, end_date: date):
        self.product_ids = product_ids
        self.start_date = start_date
        self.end_date = end_date

    def perform(self):
        self.clean_up_existing_configurations()

    def clean_up_existing_configurations(self):
        ProductAvailabilityConfiguration.objects.filter(
            product_id__in=self.product_ids,
            day__gte=self.start_date,
            day__lte=self.end_date,
        ).delete()

from datetime import date

from app.base.service import BaseService
from app.product.models import ProductAvailabilityConfiguration


class UnblockProductAvailabilityService(BaseService):
    def __init__(self, product_ids: list[int], start_date: date, end_date: date):
        self.product_ids = product_ids
        self.start_date = start_date
        self.end_date = end_date

    def perform(self):
        if self.product_ids:
            self.clean_up_by_product_ids()
        else:
            self.clean_up_by_time_range()
    
    def clean_up_by_time_range(self):
        ProductAvailabilityConfiguration.objects.filter(
            day__gte=self.start_date,
            day__lte=self.end_date,
        ).delete()

    def clean_up_by_product_ids(self):
        ProductAvailabilityConfiguration.objects.filter(
            product_id__in=self.product_ids,
            day__gte=self.start_date,
            day__lte=self.end_date,
        ).delete()

from datetime import date, datetime, timedelta
from venv import logger

from app.base.service import BaseService

from app.product.models import ProductAvailabilityConfiguration
from app.product.services.product_availability.precompute_product_availability_service import PrecomputeProductAvailabilityService
from app.product.schemas import ComputedProductAvailability


PRODUCT_AVAILABILITY_CONFIGURATION_CACHE_KEY = 'product_availability_configuration'
COMPUTED_PRODUCT_IDS_KEY = 'computed_product_availability:product_ids'
CACHE_TTL = 60 * 60 * 24


class CheckTimeRangeAvailabilityService(BaseService):
    def __init__(self, start_date: date, end_date: date):
        self.start_date = start_date
        self.end_date = end_date
        
    def perform(self) -> dict[date, list[ComputedProductAvailability]]:
        self.product_ids = self.get_product_ids()
        if not self.product_ids:
            return {}

        return PrecomputeProductAvailabilityService(
            product_ids=self.product_ids,
            start_date=self.start_date,
            end_date=self.end_date,
        ).perform()
        
    def get_product_ids(self) -> list[int]:
        return ProductAvailabilityConfiguration.objects.filter(
            day__gte=self.start_date,
            day__lte=self.end_date,
        ).values_list('product_id', flat=True)

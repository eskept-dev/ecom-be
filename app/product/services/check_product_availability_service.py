from datetime import date, datetime, timedelta
from venv import logger

from app.base.service import BaseService

from app.product.services.precompute_product_availability_service import PrecomputeProductAvailabilityService
from app.product.services.schemas import ComputedProductAvailability


PRODUCT_AVAILABILITY_CONFIGURATION_CACHE_KEY = 'product_availability_configuration'
COMPUTED_PRODUCT_IDS_KEY = 'computed_product_availability:product_ids'
CACHE_TTL = 60 * 60 * 24


class CheckProductAvailabilityService(BaseService):
    def __init__(self, product_ids: list[int], start_date: date, end_date: date):
        self.product_ids = product_ids
        self.start_date = start_date
        self.end_date = end_date
        
    def perform(self) -> dict[date, list[ComputedProductAvailability]]:
        return PrecomputeProductAvailabilityService(
            product_ids=self.product_ids,
            start_date=self.start_date,
            end_date=self.end_date,
        ).perform()

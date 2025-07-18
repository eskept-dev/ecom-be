from datetime import date, datetime, timedelta
from venv import logger

from app.base.service import BaseService

from app.product.services.precompute_product_availability_service import PrecomputeProductAvailabilityService
from app.product.services.schemas import ComputedProductAvailability


PRODUCT_AVAILABILITY_CONFIGURATION_CACHE_KEY = 'product_availability_configuration'
COMPUTED_PRODUCT_IDS_KEY = 'computed_product_availability:product_ids'
CACHE_TTL = 60 * 60 * 24


class GetProductAvailabilityService(BaseService):
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

    # def perform(self) -> dict[date, list[ComputedProductAvailability]]:
    #     self.load_cached_date()
        
    #     if self.to_compute:
    #         self.compute_missing_date()
            
    #     return self.result

    # def load_cached_date(self):
    #     self.result = {}
    #     self.to_compute = {}
        
    #     day = self.start_date
    #     while day <= self.end_date:
    #         self.get_cached_data(day)
    #         day += timedelta(days=1)
            
    # def get_cached_data(self, day: date) -> list[ComputedProductAvailability]:
    #     cached_data = PrecomputeProductAvailabilityService.get_a_day_from_cache(day)
            
    #     if not cached_data:
    #         self.to_compute[day] = []
    #         return

    #     cached_product_ids = set(cached_data.keys())
    #     matched_product_ids = cached_product_ids & set(str(product_id) for product_id in self.product_ids)
    #     cached_data = [
    #         cached_data[product_id]
    #         for product_id in matched_product_ids
    #     ]

    #     self.result[day] = cached_data

    # def compute_missing_date(self):
    #     days = list(self.to_compute.keys())

    #     logger.info(f"Days: {days}")
    #     logger.info(f"Product ids: {self.product_ids}")
        
    #     result = PrecomputeProductAvailabilityService(
    #         product_ids=self.product_ids,
    #         days=days,
    #     ).perform()
        
    #     self.result.update(result)

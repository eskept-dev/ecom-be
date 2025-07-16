from datetime import date
from django.core.cache import cache

from app.core.utils.logger import logger
from app.base.service import BaseService
from app.product.models import Product
from app.product.services.schemas import ProductAvailability


PRECOMPUTE_PRODUCT_AVAILABILITY_CACHE_KEY = "precompute_product_availability"
CACHE_TIMEOUT = 60 * 60 * 24

class PrecomputeProductAvailabilityService(BaseService):
    def __init__(self, product_ids: list[int] = None, start_date: date = None, end_date: date = None):
        self.product_ids = product_ids or []
        self.start_date = start_date
        self.end_date = end_date
        
    def perform(self) -> dict[str, ProductAvailability]:
        pass

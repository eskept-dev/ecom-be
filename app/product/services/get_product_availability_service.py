from datetime import date

from app.base.service import BaseService
from app.product.services.schemas import ProductAvailability


class GetProductAvailabilityService(BaseService):
    def __init__(self, product_ids: list[int], start_date: date, end_date: date):
        self.product_ids = product_ids
        self.start_date = start_date
        self.end_date = end_date
        
    def perform(self) -> dict[str, ProductAvailability]:
        pass

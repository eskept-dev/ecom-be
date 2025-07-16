from django.core.cache import cache

from app.base.service import BaseService

from app.product.services.schemas import AppliedProductPrice
from app.product.services.precompute_product_price_service import (
    PRECOMPUTE_PRODUCT_PRICE_CACHE_KEY,
    PrecomputeProductPriceService,
)


class GetAppliedPriceConfigurationProductService(BaseService):
    def __init__(self, product_id: int = None, product_ids: list[int] = None):
        self.product_id = product_id
        self.product_ids = product_ids or []

        if not self.product_id and not self.product_ids:
            raise ValueError("Either product_id or product_ids must be provided")
        
    def perform(self) -> AppliedProductPrice:
        if self.product_ids:
            return self.perform_multiple()
        else:
            return self.perform_single()

    def perform_single(self) -> AppliedProductPrice:
        applied_product_prices = self.get_cached_applied_product_prices()

        if not applied_product_prices or not applied_product_prices.get(str(self.product_id), None):
            applied_product_prices = PrecomputeProductPriceService(product_ids=[self.product_id]).perform()
            
        applied_product_price = applied_product_prices.get(str(self.product_id), None)

        if not applied_product_price:
            raise Exception("Applied product price not found")

        return applied_product_price
    
    def perform_multiple(self) -> dict[str, AppliedProductPrice]:
        applied_product_prices = self.get_cached_applied_product_prices()

        for product_id in self.product_ids:
            if str(product_id) not in applied_product_prices.keys():
                applied_product_prices = PrecomputeProductPriceService(product_ids=self.product_ids).perform()
                break

        return {
            str(product_id): applied_product_prices.get(str(product_id), None)
            for product_id in self.product_ids
        }

    def get_cached_applied_product_prices(self) -> dict[str, AppliedProductPrice]:
        return cache.get(f"{PRECOMPUTE_PRODUCT_PRICE_CACHE_KEY}") or {}

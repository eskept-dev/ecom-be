from django.core.cache import cache

from app.core.utils.logger import logger
from app.base.service import BaseService

from app.product.models import Product
from app.product.services.schemas import AppliedProductPrice
from app.product.services.price_configuration_helpers import (
    list_price_configurations_by_products,
    select_optimal_price_configuration,
)


PRECOMPUTE_PRODUCT_PRICE_CACHE_KEY = "precompute_product_price"
CACHE_TIMEOUT = 60 * 60 * 24

class PrecomputeProductPriceService(BaseService):
    def __init__(self, product_ids: list[int] = None):
        self.product_ids = product_ids or []

    def perform(self) -> dict[str, AppliedProductPrice]:
        self.products = self.get_products()
        logger.info(f"Found {len(self.products)} products to precompute price")

        self.all_price_configurations = list_price_configurations_by_products(self.products)
        
        new_applied_product_prices = self.get_applicable_price_configurations()

        self.store_cache(new_applied_product_prices)
        logger.info(f"Precomputed product price for {len(new_applied_product_prices)} products successfully")
        
        return self.applied_product_prices

    def get_products(self) -> list[Product]:
        query = Product.objects.filter(is_deleted=False)

        if self.product_ids:
            query = query.filter(id__in=self.product_ids)

        return query

    def get_applicable_price_configurations(self) -> dict[str, AppliedProductPrice]:
        applied_product_prices = {
            str(product.id): None for product in self.products
        }

        for product in self.products:
            potential_price_configurations = self.all_price_configurations.get(str(product.id), []) + self.all_price_configurations.get('all', [])
            
            optimal_price_configuration = select_optimal_price_configuration(product, potential_price_configurations)
            
            applied_product_prices[str(product.id)] = optimal_price_configuration
            
        return applied_product_prices

    def store_cache(self, new_applied_product_prices: dict[str, AppliedProductPrice]) -> None:
        self.applied_product_prices = self.get_cached_applied_product_prices()
        self.applied_product_prices.update(new_applied_product_prices)

        cache.set(
            f"{PRECOMPUTE_PRODUCT_PRICE_CACHE_KEY}",
            self.applied_product_prices,
            timeout=CACHE_TIMEOUT,
        )

    def get_cached_applied_product_prices(self) -> dict[str, AppliedProductPrice]:
        return cache.get(f"{PRECOMPUTE_PRODUCT_PRICE_CACHE_KEY}") or {}

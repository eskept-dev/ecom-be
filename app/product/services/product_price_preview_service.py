from app.base.service import BaseService
from app.product.services.price_configuration_helpers import (
    select_optimal_price_configuration,
    list_price_configurations_by_product_ids,
)
from app.product.services.schemas import AppliedProductPrice


class ProductPricePreviewService(BaseService):
    def __init__(self, product_ids: list[int]):
        self.product_ids = product_ids

    def perform(self) -> list[AppliedProductPrice]:
        classified_price_configurations = list_price_configurations_by_product_ids(self.product_ids)
        
        applied_product_prices = []
        for product_id in self.product_ids:
            price_configuration_ids = classified_price_configurations[str(product_id)] + classified_price_configurations['all']

            optimal_price_configuration = select_optimal_price_configuration(product_id, price_configuration_ids)

            applied_product_prices.append(optimal_price_configuration)

        return applied_product_prices

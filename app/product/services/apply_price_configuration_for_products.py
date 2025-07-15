from app.base.service import BaseService
from app.product.services.schemas import AppliedProductPrice
from app.product.services.price_configuration_helpers import (
    list_price_configurations_by_product_ids,
    select_optimal_price_configuration,
)


class ApplyPriceConfigurationForProductsService(BaseService):
    def __init__(self, product_ids: list[int]):
        self.product_ids = product_ids
        
    def perform(self) -> AppliedProductPrice:
        return self.apply()

    def apply(self) -> AppliedProductPrice:
        classified_price_configurations_ids = list_price_configurations_by_product_ids(self.product_ids)

        applied_product_prices = {}
        for product_id in self.product_ids:
            price_configuration_ids = classified_price_configurations_ids[str(product_id)] + classified_price_configurations_ids['all']

            optimal_price_configuration = select_optimal_price_configuration(product_id, price_configuration_ids)

            applied_product_prices[str(product_id)] = optimal_price_configuration

        return applied_product_prices


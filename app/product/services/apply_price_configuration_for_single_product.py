from app.base.service import BaseService
from app.product.services.schemas import AppliedProductPrice
from app.product.services.price_configuration_helpers import (
    get_price_configuration_ids_by_product_id,
    select_optimal_price_configuration,
)


class ApplyPriceConfigurationForSingleProductService(BaseService):
    def __init__(self, product_id: int):
        self.product_id = product_id
        
    def perform(self) -> AppliedProductPrice:
        return self.apply()

    def apply(self) -> AppliedProductPrice:
        price_configuration_ids = get_price_configuration_ids_by_product_id(self.product_id)

        applied_product_price = select_optimal_price_configuration(self.product_id, price_configuration_ids)
        
        return applied_product_price

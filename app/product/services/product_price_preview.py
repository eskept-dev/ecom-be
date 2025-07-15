from .price_configuration import (
    select_optimal_price_configuration,
    AppliedProductPrice,
    list_price_configurations_by_product_ids,
)


def product_price_preview(product_ids: list[int]) -> list[AppliedProductPrice]:
    classified_price_configurations = list_price_configurations_by_product_ids(product_ids)
    
    applied_product_prices = []
    for product_id in product_ids:
        price_configuration_ids = classified_price_configurations[str(product_id)] + classified_price_configurations['all']

        optimal_price_configuration = select_optimal_price_configuration(product_id, price_configuration_ids)

        applied_product_prices.append(optimal_price_configuration)

    return applied_product_prices

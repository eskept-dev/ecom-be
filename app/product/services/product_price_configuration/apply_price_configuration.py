from datetime import datetime

from app.product.models import ProductPriceConfiguration, Product
from app.product.models.price_configuration import (
    PriceAdjustmentType,
    PriceAdjustmentTimeRangeType,
)
from app.product.schemas import AppliedProductPrice


def apply_price_configuration(product: Product, price_configuration: ProductPriceConfiguration) -> AppliedProductPrice:
    """
    This function will apply the price configuration to the product
    Input:
        product_id: int
        price_configuration_id: int
    Output:
        AppliedProductPrice
    """
    if not price_configuration.is_time_range_valid():
        raise Exception("Price configuration time range is not valid")
    
    if price_configuration.adjustment_type == PriceAdjustmentType.PERCENTAGE:
        return apply_percentage_adjustment(product, price_configuration)
    
    if price_configuration.adjustment_type == PriceAdjustmentType.FIXED:
        return apply_fixed_adjustment(product, price_configuration)


def apply_fixed_adjustment(product: Product, price_configuration: ProductPriceConfiguration) -> AppliedProductPrice:
    """
    This function will apply the fixed adjustment to the product
    Input:
        product: Product
        price_configuration: ProductPriceConfiguration
    Output:
        AppliedProductPrice
    """
    price_vnd = float(product.base_price_vnd) + float(price_configuration.adjustment_value.get('fixed_vnd', 0))
    price_usd = float(product.base_price_usd) + float(price_configuration.adjustment_value.get('fixed_usd', 0))

    return AppliedProductPrice(
        product_id=product.id,
        product_name=product.name,
        price_configuration_id=price_configuration.id,
        price_configuration_name=price_configuration.name,
        base_price_vnd=product.base_price_vnd,
        price_vnd=price_vnd,
        base_price_usd=product.base_price_usd,
        price_usd=price_usd,
    )


def apply_percentage_adjustment(product: Product, price_configuration: ProductPriceConfiguration) -> AppliedProductPrice:
    """
    This function will apply the percentage adjustment to the product
    Input:
        product: Product
        price_configuration: ProductPriceConfiguration
    Output:
        AppliedProductPrice
    """
    price_vnd = float(product.base_price_vnd) * (1 + float(price_configuration.adjustment_value.get('percentage', 0)) / 100)
    price_usd = float(product.base_price_usd) * (1 + float(price_configuration.adjustment_value.get('percentage', 0)) / 100)
    
    return AppliedProductPrice(
        product_id=product.id,
        product_name=product.name,
        price_configuration_id=price_configuration.id,
        price_configuration_name=price_configuration.name,
        base_price_vnd=product.base_price_vnd,
        price_vnd=price_vnd,
        base_price_usd=product.base_price_usd,
        price_usd=price_usd,
    )

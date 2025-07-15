from dataclasses import dataclass

from app.product.models import ProductPriceConfiguration, Product
from app.product.models.price_configuration import PriceAdjustmentType
from app.product.services.schemas import AppliedProductPrice


def get_price_configuration_ids_by_product_id(product_id: int) -> list[int]:
    """
    This function will get the price configuration for a given product
    Input:
        product_ids: list[int]
    Output:
        list[int]
    """
    result = []

    price_configurations = ProductPriceConfiguration.objects.filter(
        is_active=True,
    )
    
    for price_configuration in price_configurations:
        if price_configuration.products.count() == 0:
            result.append(price_configuration.id)
        else:
            if price_configuration.products.filter(id=product_id).exists():
                result.append(price_configuration.id)
                break

    return result

    
def list_price_configurations_by_product_ids(product_ids: list[int]) -> dict:
    """
    This function will list all price configurations that are active and not associated with any product
    Output will be a dictionary with the following structure:
    {
        'all': [price_configuration_id],
        '<product_id>': [price_configuration_id],
        ...
    }
    """
    
    price_configurations = ProductPriceConfiguration.objects.filter(
        is_active=True,
    )
    
    result = {str(product_id): [] for product_id in product_ids}
    result['all'] = []

    for price_configuration in price_configurations:
        if price_configuration.products.count() == 0:
            result['all'].append(price_configuration.id)
        else:
            for product_id in product_ids:
                if price_configuration.products.filter(id=product_id).exists():
                    result[str(product_id)].append(price_configuration.id)
                    break

    return result


def apply_price_configuration(product_id: int, price_configuration_id: int) -> AppliedProductPrice:
    """
    This function will apply the price configuration to the product
    Input:
        product_id: int
        price_configuration_id: int
    Output:
        AppliedProductPrice
    """
    
    price_configuration = ProductPriceConfiguration.objects.get(id=price_configuration_id)
    product = Product.objects.get(id=product_id)
    
    if price_configuration.adjustment_type == PriceAdjustmentType.PERCENTAGE:
        return apply_percentage_adjustment(product, price_configuration)
    
    if price_configuration.adjustment_type == PriceAdjustmentType.FIXED:
        return apply_fixed_adjustment(product, price_configuration)
    

def select_optimal_price_configuration(product_id: int, price_configuration_ids: list[int]) -> AppliedProductPrice:
    """
    This function will select the optimal price configuration for a given product
    Input:
        product_id: int
        price_configuration_ids: list[int]
    Output:
        AppliedProductPrice
    """
    
    optimal_applied_product_price = None
    
    for price_configuration_id in price_configuration_ids:
        applied_product_price = apply_price_configuration(product_id, price_configuration_id)
        
        if optimal_applied_product_price is None:
            optimal_applied_product_price = applied_product_price
        else:
            if applied_product_price.price_vnd < optimal_applied_product_price.price_vnd:
                optimal_applied_product_price = applied_product_price
            elif applied_product_price.price_vnd == optimal_applied_product_price.price_vnd and applied_product_price.price_usd < optimal_applied_product_price.price_usd:
                optimal_applied_product_price = applied_product_price

    return optimal_applied_product_price


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

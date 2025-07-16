from app.core.utils.logger import logger

from app.product.models import ProductPriceConfiguration, Product
from app.product.services.apply_price_configuration import apply_price_configuration
from app.product.services.schemas import AppliedProductPrice


def get_price_configurations_by_product(product: Product) -> list[ProductPriceConfiguration]:
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
            result.append(price_configuration)
        else:
            if price_configuration.products.filter(id=product.id).exists():
                result.append(price_configuration)
                break

    return result

    
def list_price_configurations_by_products(products: list[Product]) -> dict[str, list[ProductPriceConfiguration]]:
    """
    This function will list all price configurations that are active and not associated with any product
    Output will be a dictionary with the following structure:
    {
        'all': [price_configuration],
        '<product_id>': [price_configuration],
        ...
    }
    """
    
    price_configurations = ProductPriceConfiguration.objects.filter(
        is_active=True,
    )
    
    result = {str(product.id): [] for product in products}
    result['all'] = []

    for price_configuration in price_configurations:
        if price_configuration.products.count() == 0:
            result['all'].append(price_configuration)
        else:
            for product in products:
                if price_configuration.products.filter(id=product.id).exists():
                    result[str(product.id)].append(price_configuration)
                    break

    return result


def select_optimal_price_configuration(product: Product, price_configurations: list[ProductPriceConfiguration]) -> AppliedProductPrice:
    """
    This function will select the optimal price configuration for a given product
    Input:
        product: Product
        price_configurations: list[ProductPriceConfiguration]
    Output:
        AppliedProductPrice
    """
    
    optimal_applied_product_price = None
    
    for price_configuration in price_configurations:
        try:
            applied_product_price = apply_price_configuration(product, price_configuration)
        except Exception as e:
            logger.error(f"Error applying price configuration {price_configuration.id} to product {product.id}: {e}")
            continue
        
        if optimal_applied_product_price is None:
            optimal_applied_product_price = applied_product_price
        else:
            if applied_product_price.price_vnd < optimal_applied_product_price.price_vnd:
                optimal_applied_product_price = applied_product_price
            elif applied_product_price.price_vnd == optimal_applied_product_price.price_vnd and applied_product_price.price_usd < optimal_applied_product_price.price_usd:
                optimal_applied_product_price = applied_product_price

    return optimal_applied_product_price

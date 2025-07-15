from app.core.utils.logger import logger
from app.product.models import Product
from app.product.services.schemas import AppliedProductPrice
from app.product.services.price_configuration import (
    apply_price_configuration_to_product,
    apply_price_configuration_to_products
)


def list_applied_product_prices(product_ids: list[int]) -> list[AppliedProductPrice]:
    products = Product.objects.filter(id__in=product_ids)
    if products.count() != len(product_ids):
        raise Product.DoesNotExist
    
    return apply_price_configuration_to_products(products)


def get_applied_product_price(product_id: int) -> AppliedProductPrice:
    product = Product.objects.filter(id=product_id).first()
    if not product:
        raise Product.DoesNotExist    

    applied_product_price: AppliedProductPrice = apply_price_configuration_to_product(product.id)

    return applied_product_price

from datetime import date
from dataclasses import dataclass

from app.product.models import Product, ProductAvailabilityConfiguration


@dataclass
class AppliedProductPrice:
    product_id: int
    product_name: str
    price_configuration_id: int
    price_configuration_name: str
    base_price_vnd: float
    price_vnd: float
    base_price_usd: float
    price_usd: float


@dataclass
class ProductAvailability:
    product_id: int
    product_name: str
    booking_count: int = 0
    max_capacity: int = 0


@dataclass
class ComputedProductAvailability:
    product: Product
    availability_configuration: ProductAvailabilityConfiguration
    max_capacity: int

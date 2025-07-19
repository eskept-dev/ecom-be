from datetime import date

from app.base.service import BaseService
from app.product.models import (
    ProductAvailabilityConfiguration,
    ProductAvailabilityConfigurationType,
    Product,
)
from app.product.schemas import ComputedProductAvailability


class ComputeProductAvailabilityService(BaseService):
    def __init__(self, product: Product, product_availability_configuration: ProductAvailabilityConfiguration):
        self.product = product
        self.product_availability_configuration = product_availability_configuration
        
    def perform(self) -> ComputedProductAvailability:
        if self.product_availability_configuration.type == ProductAvailabilityConfigurationType.FIXED_QUANTITY:
            return self.perform_fixed_quantity()
        elif self.product_availability_configuration.type == ProductAvailabilityConfigurationType.PERCENTAGE_QUANTITY:
            return self.perform_percentage_quantity()
        elif self.product_availability_configuration.type == ProductAvailabilityConfigurationType.BLOCK:
            return self.perform_block()
        elif self.product_availability_configuration.type == ProductAvailabilityConfigurationType.NO_LIMIT:
            return self.perform_no_limit()
        else:
            raise ValueError(f"Invalid product availability configuration type: {self.product_availability_configuration.type}")

    def perform_fixed_quantity(self) -> ComputedProductAvailability:
        return ComputedProductAvailability(
            product=self.product,
            availability_configuration=self.product_availability_configuration,
            max_capacity=self.product_availability_configuration.value,
        )

    def perform_percentage_quantity(self) -> ComputedProductAvailability:
        max_capacity = max(round(self.product.max_quantity * self.product_availability_configuration.value / 100))
        
        return ComputedProductAvailability(
            product=self.product,
            availability_configuration=self.product_availability_configuration,
            max_capacity=max_capacity,
        )

    def perform_block(self) -> ComputedProductAvailability:
        return ComputedProductAvailability(
            product=self.product,
            availability_configuration=self.product_availability_configuration,
            max_capacity=0,
        )
        
    def perform_no_limit(self) -> ComputedProductAvailability:
        return ComputedProductAvailability(
            product=self.product,
            availability_configuration=self.product_availability_configuration,
            max_capacity=ProductAvailabilityConfiguration.NO_LIMIT_MAX_CAPACITY,
        )

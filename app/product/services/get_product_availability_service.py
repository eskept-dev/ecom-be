from datetime import date, timedelta

from app.base.service import BaseService
from app.core.utils.logger import logger

from app.product.models import ProductAvailabilityConfiguration, Product
from app.product.services.compute_product_availability_service import ComputeProductAvailabilityService
from app.product.services.schemas import ComputedProductAvailability


class GetProductAvailabilityService(BaseService):
    def __init__(self, product_ids: list[int], start_date: date, end_date: date):
        self.product_ids = product_ids
        self.start_date = start_date
        self.end_date = end_date
        
    def perform(self) -> dict[date, ComputedProductAvailability]:
        product_availability_configurations = self.list_product_availability_configurations()
        logger.info(f"Found {len(product_availability_configurations)} product availability configurations")
        if not product_availability_configurations:
            return {}
        
        computed_product_availability_calendars_by_day: dict[date, ComputedProductAvailability] = {}
        for i in range((self.end_date - self.start_date).days + 1):
            day = self.start_date + timedelta(days=i)
            logger.info(f"Processing day: {day}".center(100, "="))
            computed_product_availability_calendars_by_day[day] = []

            for product_id in self.product_ids:
                logger.info(f"Processing product: {product_id}")
                product = Product.objects.get(id=product_id)
                product_availability_configuration = self.select_effective_product_availability_configuration(product, product_availability_configurations)
                computed_product_availability = ComputeProductAvailabilityService(
                    product=product,
                    product_availability_configuration=product_availability_configuration,
                ).perform()

                logger.info(f"The most effective product availability configuration for product {product_id} is: {computed_product_availability}")
                computed_product_availability_calendars_by_day[day].append(computed_product_availability)
        
        return computed_product_availability_calendars_by_day
    
    def list_product_availability_configurations(self) -> list[ProductAvailabilityConfiguration]:
        return ProductAvailabilityConfiguration.objects.filter(
            products__in=self.product_ids,
            start_date__lte=self.end_date,
            end_date__gte=self.start_date,
        ).all()
        
    def select_effective_product_availability_configuration(
        self,
        product: Product,
        list_product_availability_configurations: list[ProductAvailabilityConfiguration],
    ) -> ProductAvailabilityConfiguration:
        max_capacity = ProductAvailabilityConfiguration.NO_LIMIT_MAX_CAPACITY
        effective_product_availability_configuration = None
        
        for product_availability_configuration in list_product_availability_configurations:
            computed_product_availability = ComputeProductAvailabilityService(
                product=product,
                product_availability_configuration=product_availability_configuration,
            ).perform()
            
            if computed_product_availability.max_capacity <= max_capacity:
                effective_product_availability_configuration = product_availability_configuration
                max_capacity = computed_product_availability.max_capacity
        
        return effective_product_availability_configuration
